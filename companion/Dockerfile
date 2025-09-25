FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json pnpm-lock.yaml ./
COPY schemas/ ./schemas/

# Install pnpm
RUN npm install -g pnpm

# Install dependencies
RUN pnpm install

# Copy source code
COPY . .

# Build the application
RUN pnpm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["pnpm", "start"]
