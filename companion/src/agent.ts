import { 
  AgentRequest, 
  AgentResponse, 
  LegacyActionPlan as ActionPlan, 
  Action, 
  DeviceInfo,
  LLMRequest,
  LLMProvider
} from '@ezra/schemas';
import { LLMRouter } from './llm';
import { CryptoService } from './crypto';

export class AgentService {
  constructor(
    private llmRouter: LLMRouter,
    private cryptoService: CryptoService
  ) {}

  async processRequest(request: AgentRequest): Promise<AgentResponse> {
    // Generate action plan using LLM
    const actionPlan = await this.generateActionPlan(request);
    
    // Sign the action plan
    const signedPlan = this.cryptoService.signData(actionPlan);
    
    // Generate human-readable summary
    const summary = this.generateHumanSummary(actionPlan);
    
    // Determine if consent is required
    const consentRequired = actionPlan.actions.some((action: Action) => 
      action.requires_consent || action.risk_level === 'high' || action.risk_level === 'critical'
    );
    
    // Calculate overall risk level
    const estimatedRisk = this.calculateOverallRisk(actionPlan.actions);

    return {
      action_plan: signedPlan.data,
      human_readable_summary: summary,
      consent_required: consentRequired,
      estimated_risk: estimatedRisk,
    };
  }

  private async generateActionPlan(request: AgentRequest): Promise<ActionPlan> {
    const systemPrompt = this.buildSystemPrompt(request.device_info);
    const userPrompt = this.buildUserPrompt(request);

    // Select best LLM provider for this task
    const provider = this.llmRouter.getBestProvider(request.user_prompt);
    
    const llmRequest: LLMRequest = {
      provider,
      model: this.getModelForProvider(provider),
      prompt: userPrompt,
      system_prompt: systemPrompt,
      max_tokens: 4000,
      temperature: 0.7,
    };

    const response = await this.llmRouter.generate(llmRequest);
    
    // Parse the LLM response into structured actions
    const actions = this.parseActionsFromResponse(response.content, request.device_info);
    
    return {
      id: this.generatePlanId(),
      device_id: request.device_info.id,
      created_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24 hours
      actions,
      signature: '', // Will be filled by signing
      metadata: {
        llm_provider: provider,
        model: llmRequest.model,
        confidence: response.metadata.confidence || 0.5,
        reasoning: response.content,
      },
    };
  }

  private buildSystemPrompt(deviceInfo: DeviceInfo): string {
    return `You are Ezra, a universal system agent. You generate action plans for device management tasks.

Device Information:
- Platform: ${deviceInfo.platform}
- OS: ${deviceInfo.os} ${deviceInfo.version}
- Architecture: ${deviceInfo.architecture}
- Hardware: ${JSON.stringify(deviceInfo.hardware)}
- Capabilities: ${deviceInfo.capabilities.join(', ')}

You can perform these types of actions:
- install: Install software/packages
- configure: Modify system settings
- modify: Change files or configurations
- backup: Create backups before changes
- restore: Restore from backups
- jailbreak: Bypass security restrictions (high risk)
- bypass: Circumvent DRM or restrictions (high risk)

Risk levels:
- low: Safe operations like reading files
- medium: System modifications that can be undone
- high: Permanent changes or security bypasses
- critical: Operations that could brick the device

Always include rollback commands for high/critical risk operations.
Always require explicit consent for high/critical risk operations.

Respond with a JSON array of actions, each with:
- id: unique identifier
- type: action type
- description: human-readable description
- risk_level: low/medium/high/critical
- requires_consent: boolean
- commands: array of shell commands to execute
- rollback_commands: array of commands to undo (optional)
- dependencies: array of prerequisite actions (optional)
- estimated_duration: seconds (optional)`;
  }

  private buildUserPrompt(request: AgentRequest): string {
    let prompt = `User request: ${request.user_prompt}\n\n`;
    
    if (request.context?.previous_actions) {
      prompt += `Previous actions: ${request.context.previous_actions.join(', ')}\n\n`;
    }
    
    if (request.context?.constraints) {
      prompt += `Constraints: ${request.context.constraints.join(', ')}\n\n`;
    }
    
    prompt += `Generate an action plan to fulfill this request. Consider the device capabilities and platform.`;
    
    return prompt;
  }

  private parseActionsFromResponse(response: string, deviceInfo: DeviceInfo): Action[] {
    try {
      // Try to extract JSON from the response
      const jsonMatch = response.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        const actions = JSON.parse(jsonMatch[0]);
        return actions.map((action: Record<string, any>, index: number) => ({
          id: action.id || `action_${index}`,
          type: action.type,
          description: action.description,
          risk_level: action.risk_level,
          requires_consent: action.requires_consent || false,
          commands: action.commands || [],
          rollback_commands: action.rollback_commands,
          dependencies: action.dependencies,
          estimated_duration: action.estimated_duration,
        }));
      }
    } catch (error) {
      console.warn('Failed to parse LLM response as JSON:', error);
    }

    // Fallback: generate a simple action plan
    return [{
      id: 'fallback_action',
      type: 'configure',
      description: 'Execute user request with basic system commands',
      risk_level: 'medium',
      requires_consent: true,
      commands: [`echo "Executing: ${response}"`],
      estimated_duration: 30,
    }];
  }

  private generatePlanId(): string {
    return `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getModelForProvider(provider: LLMProvider): string {
    switch (provider) {
      case 'openai':
        return 'gpt-4';
      case 'anthropic':
        return 'claude-3-sonnet';
      case 'google':
        return 'gemini-pro';
      default:
        return 'gpt-4';
    }
  }

  private generateHumanSummary(plan: ActionPlan): string {
    const actionCount = plan.actions.length;
    const riskLevels = plan.actions.map((a: Action) => a.risk_level);
    const highRiskCount = riskLevels.filter((r: string) => r === 'high' || r === 'critical').length;
    
    let summary = `This plan includes ${actionCount} action(s)`;
    
    if (highRiskCount > 0) {
      summary += `, with ${highRiskCount} high-risk operation(s)`;
    }
    
    summary += `. The plan will:`;
    
    plan.actions.forEach((action: Action, index: number) => {
      summary += `\n${index + 1}. ${action.description} (${action.risk_level} risk)`;
    });
    
    return summary;
  }

  private calculateOverallRisk(actions: Action[]): 'low' | 'medium' | 'high' | 'critical' {
    const riskLevels = actions.map(a => a.risk_level);
    
    if (riskLevels.includes('critical')) return 'critical';
    if (riskLevels.includes('high')) return 'high';
    if (riskLevels.includes('medium')) return 'medium';
    return 'low';
  }
}
