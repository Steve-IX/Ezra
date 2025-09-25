FROM node:20-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy workspace files
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./

# Copy schemas first (dependency)
COPY schemas/ ./schemas/

# Copy companion package files
COPY companion/package.json ./companion/

# Install dependencies
RUN pnpm install

# Copy companion source code
COPY companion/ ./companion/

# Build the application
RUN cd companion && pnpm run build

# Expose port
EXPOSE 3000

# Start the application
WORKDIR /app/companion
CMD ["pnpm", "start"]
