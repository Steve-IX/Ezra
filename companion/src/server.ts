import Fastify, { FastifyInstance } from 'fastify';
import cors from '@fastify/cors';
import helmet from '@fastify/helmet';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import { 
  AgentRequestSchema, 
  AgentResponseSchema, 
  DeviceInfoSchema,
  CompanionConfigSchema,
  AgentRequest,
  Signature
} from '@ezra/schemas';
import { AgentService } from './agent';
import { LLMRouter } from './llm';
import { CryptoService } from './crypto';

export class CompanionServer {
  private fastify: FastifyInstance;
  private agentService: AgentService;
  private cryptoService: CryptoService;
  private llmRouter: LLMRouter;

  constructor(private config: any) {
    this.fastify = Fastify({
      logger: {
        level: 'info',
        transport: {
          target: 'pino-pretty',
          options: {
            colorize: true,
          },
        },
      },
    });

    this.cryptoService = new CryptoService(config.signing?.private_key);
    this.llmRouter = new LLMRouter();
    this.agentService = new AgentService(this.llmRouter, this.cryptoService);

    this.setupPlugins();
    this.setupRoutes();
  }

  private async setupPlugins() {
    // CORS
    await this.fastify.register(cors, {
      origin: true,
      credentials: true,
    });

    // Security headers
    await this.fastify.register(helmet);

    // Swagger documentation
    await this.fastify.register(swagger, {
      swagger: {
        info: {
          title: 'Ezra Companion API',
          description: 'Universal system agent companion server',
          version: '0.1.0',
        },
        host: 'localhost:3000',
        schemes: ['http', 'https'],
        consumes: ['application/json'],
        produces: ['application/json'],
      },
    });

    await this.fastify.register(swaggerUi, {
      routePrefix: '/docs',
      uiConfig: {
        docExpansion: 'full',
        deepLinking: false,
      },
    });
  }

  private setupRoutes() {
    // Health check
    this.fastify.get('/health', async (request, reply) => {
      return {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '0.1.0',
        providers: this.llmRouter.getAvailableProviders(),
      };
    });

    // Generate action plan
    this.fastify.post('/api/v1/agent/plan', {
      schema: {
        description: 'Generate an action plan for a device request',
        tags: ['agent'],
        body: AgentRequestSchema,
        response: {
          200: AgentResponseSchema,
        },
      },
    }, async (request, reply) => {
      try {
        const agentRequest = request.body as AgentRequest;
        const response = await this.agentService.processRequest(agentRequest);
        return response;
      } catch (error) {
        console.error('Error generating action plan:', error);
        reply.code(500).send({
          error: 'Failed to generate action plan',
          message: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    });

    // Verify action plan signature
    this.fastify.post('/api/v1/agent/verify', {
      schema: {
        description: 'Verify the signature of an action plan',
        tags: ['agent'],
        body: {
          type: 'object',
          properties: {
            action_plan: { type: 'object' },
            signature: { type: 'object' },
          },
          required: ['action_plan', 'signature'],
        },
      },
    }, async (request, reply) => {
      try {
        const { action_plan, signature } = request.body as { action_plan: unknown; signature: unknown };
        const isValid = this.cryptoService.verify(action_plan, signature as Signature);
        
        return {
          valid: isValid,
          timestamp: new Date().toISOString(),
        };
      } catch (error) {
        console.error('Error verifying signature:', error);
        reply.code(500).send({
          error: 'Failed to verify signature',
          message: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    });

    // Get public key for verification
    this.fastify.get('/api/v1/crypto/public-key', {
      schema: {
        description: 'Get the public key for signature verification',
        tags: ['crypto'],
        response: {
          200: {
            type: 'object',
            properties: {
              public_key: { type: 'string' },
              algorithm: { type: 'string' },
            },
          },
        },
      },
    }, async (request, reply) => {
      return {
        public_key: this.cryptoService.getPublicKey(),
        algorithm: 'ed25519',
      };
    });

    // LLM provider status
    this.fastify.get('/api/v1/llm/providers', {
      schema: {
        description: 'Get available LLM providers and their status',
        tags: ['llm'],
        response: {
          200: {
            type: 'object',
            properties: {
              providers: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    name: { type: 'string' },
                    available: { type: 'boolean' },
                    rate_limit: { type: 'object' },
                  },
                },
              },
            },
          },
        },
      },
    }, async (request, reply) => {
      const providers = this.llmRouter.getAvailableProviders();
      const providerInfo = providers.map(name => ({
        name,
        available: true,
        rate_limit: this.llmRouter['providers'].get(name)?.getRateLimit() || { requests: 0, tokens: 0 },
      }));

      return { providers: providerInfo };
    });
  }

  async start() {
    try {
      const address = await this.fastify.listen({
        port: this.config.port || 3000,
        host: this.config.host || '0.0.0.0',
      });
      
      this.fastify.log.info(`Ezra Companion Server running at ${address}`);
      this.fastify.log.info(`API documentation available at ${address}/docs`);
    } catch (error) {
      console.error('Failed to start server:', error);
      process.exit(1);
    }
  }

  async stop() {
    await this.fastify.close();
  }
}
