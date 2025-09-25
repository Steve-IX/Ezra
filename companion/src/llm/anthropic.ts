import Anthropic from '@anthropic-ai/sdk';
import { LLMRequest, LLMResponse, LLMProvider } from '@ezra/schemas';

export class AnthropicProvider {
  private client: Anthropic | null = null;
  private isConfigured = false;

  constructor() {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (apiKey) {
      this.client = new Anthropic({ apiKey });
      this.isConfigured = true;
    }
  }

  isAvailable(): boolean {
    return this.isConfigured && this.client !== null;
  }

  async generate(request: LLMRequest): Promise<LLMResponse> {
    if (!this.client) {
      throw new Error('Anthropic client not configured');
    }

    // const systemPrompt = request.system_prompt || '';
    // const fullPrompt = systemPrompt ? `${systemPrompt}\n\n${request.prompt}` : request.prompt;

    const response = await this.client.messages.create({
      model: request.model,
      max_tokens: request.max_tokens || 4096,
      temperature: request.temperature,
      system: request.system_prompt,
      messages: [
        {
          role: 'user',
          content: request.prompt,
        },
      ],
    });

    const content = response.content[0];
    if (!content || content.type !== 'text') {
      throw new Error('No text response from Anthropic');
    }

    return {
      provider: 'anthropic' as LLMProvider,
      model: request.model,
      content: content.text,
      usage: {
        prompt_tokens: response.usage.input_tokens,
        completion_tokens: response.usage.output_tokens,
        total_tokens: response.usage.input_tokens + response.usage.output_tokens,
      },
      metadata: {
        finish_reason: response.stop_reason || 'unknown',
        confidence: this.calculateConfidence(response),
      },
    };
  }

  getRateLimit(): { requests: number; tokens: number } {
    return { requests: 30, tokens: 50000 }; // Per minute
  }

  private calculateConfidence(response: Anthropic.Messages.Message): number {
    // Simple confidence calculation based on stop reason
    switch (response.stop_reason) {
      case 'end_turn':
        return 0.9;
      case 'max_tokens':
        return 0.7;
      case 'stop_sequence':
        return 0.8;
      default:
        return 0.5;
    }
  }
}
