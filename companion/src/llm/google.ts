import { GoogleGenerativeAI } from '@google/generative-ai';
import { LLMRequest, LLMResponse, LLMProvider } from '@ezra/schemas';

export class GoogleProvider {
  private client: GoogleGenerativeAI | null = null;
  private isConfigured = false;

  constructor() {
    const apiKey = process.env.GOOGLE_API_KEY;
    if (apiKey) {
      this.client = new GoogleGenerativeAI(apiKey);
      this.isConfigured = true;
    }
  }

  isAvailable(): boolean {
    return this.isConfigured && this.client !== null;
  }

  async generate(request: LLMRequest): Promise<LLMResponse> {
    if (!this.client) {
      throw new Error('Google client not configured');
    }

    const model = this.client.getGenerativeModel({ 
      model: request.model,
      generationConfig: {
        maxOutputTokens: request.max_tokens,
        temperature: request.temperature,
      },
    });

    const systemPrompt = request.system_prompt || '';
    const fullPrompt = systemPrompt ? `${systemPrompt}\n\n${request.prompt}` : request.prompt;

    const result = await model.generateContent(fullPrompt);
    const response = await result.response;
    const text = response.text();

    if (!text) {
      throw new Error('No response from Google Gemini');
    }

    // Google doesn't provide detailed usage stats in the same way
    const estimatedTokens = Math.ceil(text.length / 4); // Rough estimation

    return {
      provider: 'google' as LLMProvider,
      model: request.model,
      content: text,
      usage: {
        prompt_tokens: Math.ceil(fullPrompt.length / 4),
        completion_tokens: estimatedTokens,
        total_tokens: Math.ceil(fullPrompt.length / 4) + estimatedTokens,
      },
      metadata: {
        finish_reason: 'stop',
        confidence: this.calculateConfidence(response),
      },
    };
  }

  getRateLimit(): { requests: number; tokens: number } {
    return { requests: 60, tokens: 150000 }; // Per minute
  }

  private calculateConfidence(response: any): number {
    // Simple confidence calculation for Google Gemini
    // This is a placeholder - Google's API doesn't provide detailed confidence metrics
    return 0.8;
  }
}
