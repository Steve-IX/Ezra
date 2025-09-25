import { LLMProvider, LLMRequest, LLMResponse } from '@ezra/schemas';
import { OpenAIProvider } from './openai';
import { AnthropicProvider } from './anthropic';
import { GoogleProvider } from './google';

export interface LLMProviderInterface {
  generate(request: LLMRequest): Promise<LLMResponse>;
  isAvailable(): boolean;
  getRateLimit(): { requests: number; tokens: number };
}

export class LLMRouter {
  private providers: Map<LLMProvider, LLMProviderInterface> = new Map();

  constructor() {
    this.providers.set('openai', new OpenAIProvider());
    this.providers.set('anthropic', new AnthropicProvider());
    this.providers.set('google', new GoogleProvider());
  }

  async generate(request: LLMRequest): Promise<LLMResponse> {
    const provider = this.providers.get(request.provider);
    if (!provider) {
      throw new Error(`Unsupported LLM provider: ${request.provider}`);
    }

    if (!provider.isAvailable()) {
      throw new Error(`LLM provider ${request.provider} is not available`);
    }

    return provider.generate(request);
  }

  async generateWithFallback(request: LLMRequest, fallbackProviders: LLMProvider[] = []): Promise<LLMResponse> {
    const allProviders = [request.provider, ...fallbackProviders];
    
    for (const provider of allProviders) {
      try {
        const modifiedRequest = { ...request, provider };
        return await this.generate(modifiedRequest);
      } catch (error) {
        console.warn(`Provider ${provider} failed:`, error);
        continue;
      }
    }

    throw new Error('All LLM providers failed');
  }

  getAvailableProviders(): LLMProvider[] {
    return Array.from(this.providers.entries())
      .filter(([, provider]) => provider.isAvailable())
      .map(([name]) => name);
  }

  getBestProvider(task: string): LLMProvider {
    // Simple heuristic for provider selection
    const available = this.getAvailableProviders();
    
    if (task.includes('code') || task.includes('technical')) {
      return available.includes('openai') ? 'openai' : available[0];
    }
    
    if (task.includes('creative') || task.includes('writing')) {
      return available.includes('anthropic') ? 'anthropic' : available[0];
    }
    
    return available[0] || 'openai';
  }
}
