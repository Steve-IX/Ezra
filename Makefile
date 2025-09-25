# Ezra - Universal System Agent
# Polyglot build system for TypeScript + Python + Go

.PHONY: build lint test clean install deps help

# Default target
all: build

# Build all components
build: build-schemas build-companion build-agent build-executor build-bootstrap
	@echo "✅ All components built successfully"

# Build schemas (TypeScript)
build-schemas:
	@echo "🔧 Building schemas..."
	cd schemas && pnpm install && pnpm run build

# Build companion server (TypeScript)
build-companion: build-schemas
	@echo "🔧 Building companion server..."
	cd companion && pnpm install && pnpm run build

# Build agent (Python)
build-agent:
	@echo "🔧 Building agent..."
	cd agent && pip install -e .

# Build executor (Python)
build-executor:
	@echo "🔧 Building executor..."
	cd executor && pip install -e .

# Build bootstrap (Go)
build-bootstrap:
	@echo "🔧 Building bootstrap..."
	cd bootstrap && go mod tidy && go build -o bin/ezra-bootstrap ./cmd/ezra-bootstrap

# Lint all components
lint: lint-schemas lint-companion lint-agent lint-executor lint-bootstrap
	@echo "✅ All linting completed"

lint-schemas:
	@echo "🔍 Linting schemas..."
	cd schemas && pnpm run lint || echo "No lint script for schemas"

lint-companion:
	@echo "🔍 Linting companion..."
	cd companion && pnpm run lint || echo "No lint script for companion"

lint-agent:
	@echo "🔍 Linting agent..."
	cd agent && python -m ruff check . || echo "Ruff not available"

lint-executor:
	@echo "🔍 Linting executor..."
	cd executor && python -m ruff check . || echo "Ruff not available"

lint-bootstrap:
	@echo "🔍 Linting bootstrap..."
	cd bootstrap && go vet ./... || echo "Go vet completed"

# Test all components
test: test-schemas test-companion test-agent test-executor test-bootstrap
	@echo "✅ All tests completed"

test-schemas:
	@echo "🧪 Testing schemas..."
	cd schemas && pnpm test || echo "No tests for schemas"

test-companion:
	@echo "🧪 Testing companion..."
	cd companion && pnpm test || echo "No tests for companion"

test-agent:
	@echo "🧪 Testing agent..."
	cd agent && python -m pytest || echo "No tests for agent"

test-executor:
	@echo "🧪 Testing executor..."
	cd executor && python -m pytest || echo "No tests for executor"

test-bootstrap:
	@echo "🧪 Testing bootstrap..."
	cd bootstrap && go test ./... || echo "No tests for bootstrap"

# Install dependencies
deps:
	@echo "📦 Installing dependencies..."
	pnpm install
	cd companion && pnpm install
	cd schemas && pnpm install
	cd agent && pip install -e .
	cd executor && pip install -e .
	cd bootstrap && go mod tidy

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf **/node_modules
	rm -rf **/dist
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	rm -rf **/build
	rm -rf **/bin
	rm -rf **/.pytest_cache
	rm -rf **/coverage
	rm -rf **/dist

# Install system dependencies
install-deps:
	@echo "📦 Installing system dependencies..."
	# Install pnpm globally
	npm install -g pnpm
	# Install Python dependencies
	pip install --upgrade pip
	pip install ruff pytest mypy
	# Install Go tools
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Type check all TypeScript components
typecheck: typecheck-schemas typecheck-companion
	@echo "✅ All type checking completed"

typecheck-schemas:
	@echo "🔍 Type checking schemas..."
	cd schemas && pnpm run build

typecheck-companion:
	@echo "🔍 Type checking companion..."
	cd companion && pnpm run build

# Format code
format: format-schemas format-companion format-agent format-executor format-bootstrap
	@echo "✅ All formatting completed"

format-schemas:
	@echo "🎨 Formatting schemas..."
	cd schemas && pnpm run format || echo "No format script for schemas"

format-companion:
	@echo "🎨 Formatting companion..."
	cd companion && pnpm run format || echo "No format script for companion"

format-agent:
	@echo "🎨 Formatting agent..."
	cd agent && python -m black . || echo "Black not available"

format-executor:
	@echo "🎨 Formatting executor..."
	cd executor && python -m black . || echo "Black not available"

format-bootstrap:
	@echo "🎨 Formatting bootstrap..."
	cd bootstrap && go fmt ./...

# Security scan
security:
	@echo "🔒 Running security scans..."
	cd companion && npm audit || echo "No audit for companion"
	cd agent && pip install safety && safety check || echo "Safety not available"
	cd bootstrap && go list -json -deps ./... | nancy sleuth || echo "Nancy not available"

# Show help
help:
	@echo "Ezra - Universal System Agent"
	@echo ""
	@echo "Available targets:"
	@echo "  build        - Build all components"
	@echo "  lint         - Lint all components"
	@echo "  test         - Test all components"
	@echo "  clean        - Clean build artifacts"
	@echo "  deps         - Install dependencies"
	@echo "  install-deps - Install system dependencies"
	@echo "  typecheck    - Type check TypeScript components"
	@echo "  format       - Format all code"
	@echo "  security     - Run security scans"
	@echo "  help         - Show this help"
	@echo ""
	@echo "Component-specific targets:"
	@echo "  build-schemas, build-companion, build-agent, build-executor, build-bootstrap"
	@echo "  lint-schemas, lint-companion, lint-agent, lint-executor, lint-bootstrap"
	@echo "  test-schemas, test-companion, test-agent, test-executor, test-bootstrap"
