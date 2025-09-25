import OpenAI from 'openai';
import { LLMRequest, LLMResponse, LLMProvider } from '@ezra/schemas';

export class OpenAIProvider {
  private client: OpenAI | null = null;
  private isConfigured = false;

  constructor() {
    const apiKey = process.env.OPENAI_API_KEY;
    if (apiKey) {
      this.client = new OpenAI({ apiKey });
      this.isConfigured = true;
    }
  }

  isAvailable(): boolean {
    return this.isConfigured && this.client !== null;
  }

  async generate(request: LLMRequest): Promise<LLMResponse> {
    if (!this.client) {
      throw new Error('OpenAI client not configured');
    }

    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [];
    
    if (request.system_prompt) {
      messages.push({ role: 'system', content: request.system_prompt });
    }
    
    messages.push({ role: 'user', content: request.prompt });

    const response = await this.client.chat.completions.create({
      model: request.model,
      messages,
      max_tokens: request.max_tokens,
      temperature: request.temperature,
    });

    const choice = response.choices[0];
    if (!choice || !choice.message.content) {
      throw new Error('No response from OpenAI');
    }

    return {
      provider: 'openai' as LLMProvider,
      model: request.model,
      content: choice.message.content,
      usage: {
        prompt_tokens: response.usage?.prompt_tokens || 0,
        completion_tokens: response.usage?.completion_tokens || 0,
        total_tokens: response.usage?.total_tokens || 0,
      },
      metadata: {
        finish_reason: choice.finish_reason || 'unknown',
        confidence: this.calculateConfidence(choice),
      },
    };
  }

  getRateLimit(): { requests: number; tokens: number } {
    return { requests: 60, tokens: 100000 }; // Per minute
  }

  private calculateConfidence(choice: any): number {
    // Simple confidence calculation based on finish reason
    switch (choice.finish_reason) {
      case 'stop':
        return 0.9;
      case 'length':
        return 0.7;
      case 'content_filter':
        return 0.3;
      default:
        return 0.5;
    }
  }
}
