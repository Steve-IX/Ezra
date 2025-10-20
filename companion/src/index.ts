import { CompanionConfigSchema } from '@ezra/schemas';
import { CompanionServer } from './server';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config({ path: path.join(__dirname, '../.env') });

function checkConfiguration(): boolean {
  // Check if .env file exists
  const envPath = path.join(__dirname, '../.env');
  const configPath = process.env.EZRA_CONFIG || path.join(__dirname, '../config.json');

  if (!fs.existsSync(envPath) && !fs.existsSync(configPath)) {
    return false;
  }

  // Check if at least one API key is configured
  const hasOpenAI = !!process.env.OPENAI_API_KEY;
  const hasAnthropic = !!process.env.ANTHROPIC_API_KEY;
  const hasGoogle = !!process.env.GOOGLE_API_KEY;

  return hasOpenAI || hasAnthropic || hasGoogle;
}

async function main() {
  // Check for configuration on first run
  if (!checkConfiguration()) {
    console.error('\n❌ Error: Ezra Companion Server is not configured.');
    console.error('\n📋 Please run the setup wizard to configure API keys:');
    console.error('   pnpm setup');
    console.error('\n   Or manually create a .env file with your API keys.');
    console.error('   See .env.example for the template.\n');
    process.exit(1);
  }

  // Load configuration
  const configPath = process.env.EZRA_CONFIG || path.join(__dirname, '../config.json');
  let config: any = {};

  if (fs.existsSync(configPath)) {
    try {
      config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } catch (error) {
      console.error('Failed to load config file:', error);
      process.exit(1);
    }
  } else {
    // Use environment variables for configuration
    config = {
      port: parseInt(process.env.PORT || process.env.EZRA_PORT || '3000'),
      host: process.env.HOST || process.env.EZRA_HOST || '0.0.0.0',
      llm_providers: {
        openai: process.env.OPENAI_API_KEY ? {
          api_key: process.env.OPENAI_API_KEY,
          models: ['gpt-4', 'gpt-3.5-turbo'],
        } : undefined,
        anthropic: process.env.ANTHROPIC_API_KEY ? {
          api_key: process.env.ANTHROPIC_API_KEY,
          models: ['claude-3-opus', 'claude-3-sonnet'],
        } : undefined,
        google: process.env.GOOGLE_API_KEY ? {
          api_key: process.env.GOOGLE_API_KEY,
          models: ['gemini-pro'],
        } : undefined,
      },
      signing: {
        private_key: process.env.EZRA_PRIVATE_KEY,
        public_key: process.env.EZRA_PUBLIC_KEY,
      },
      rate_limits: {
        requests_per_minute: parseInt(process.env.RATE_LIMIT_REQUESTS_PER_MINUTE || process.env.EZRA_RATE_LIMIT_REQUESTS || '60'),
        tokens_per_minute: parseInt(process.env.RATE_LIMIT_TOKENS_PER_MINUTE || process.env.EZRA_RATE_LIMIT_TOKENS || '100000'),
      },
    };
  }

  // Validate configuration
  try {
    CompanionConfigSchema.parse(config);
  } catch (error) {
    console.error('Invalid configuration:', error);
    process.exit(1);
  }

  // Create and start server
  const server = new CompanionServer(config);

  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('Received SIGINT, shutting down gracefully...');
    await server.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('Received SIGTERM, shutting down gracefully...');
    await server.stop();
    process.exit(0);
  });

  await server.start();
}

if (require.main === module) {
  main().catch((error) => {
    console.error('Failed to start Ezra Companion Server:', error);
    process.exit(1);
  });
}
