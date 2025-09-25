# Ezra - Universal System Agent
# PowerShell build script for Windows

param(
    [string]$Target = "build",
    [switch]$Verbose
)

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Build-Schemas {
    Write-ColorOutput "🔧 Building schemas..." "Cyan"
    Set-Location schemas
    pnpm install
    pnpm run build
    Set-Location ..
}

function Build-Companion {
    Write-ColorOutput "🔧 Building companion server..." "Cyan"
    Set-Location companion
    pnpm install
    pnpm run build
    Set-Location ..
}

function Build-Agent {
    Write-ColorOutput "🔧 Building agent..." "Cyan"
    Set-Location agent
    pip install -e .
    Set-Location ..
}

function Build-Executor {
    Write-ColorOutput "🔧 Building executor..." "Cyan"
    Set-Location executor
    pip install -e .
    Set-Location ..
}

function Build-Bootstrap {
    Write-ColorOutput "🔧 Building bootstrap..." "Cyan"
    Set-Location bootstrap
    go mod tidy
    go build -o bin/ezra-bootstrap.exe ./cmd/ezra-bootstrap
    Set-Location ..
}

function Test-All {
    Write-ColorOutput "🧪 Testing all components..." "Yellow"
    
    # Test schemas
    Set-Location schemas
    pnpm test
    Set-Location ..
    
    # Test companion
    Set-Location companion
    pnpm test
    Set-Location ..
    
    # Test agent
    Set-Location agent
    python -m pytest
    Set-Location ..
    
    # Test executor
    Set-Location executor
    python -m pytest
    Set-Location ..
    
    # Test bootstrap
    Set-Location bootstrap
    go test ./...
    Set-Location ..
}

function Lint-All {
    Write-ColorOutput "🔍 Linting all components..." "Yellow"
    
    # Lint schemas
    Set-Location schemas
    pnpm run lint
    Set-Location ..
    
    # Lint companion
    Set-Location companion
    pnpm run lint
    Set-Location ..
    
    # Lint agent
    Set-Location agent
    python -m ruff check .
    Set-Location ..
    
    # Lint executor
    Set-Location executor
    python -m ruff check .
    Set-Location ..
    
    # Lint bootstrap
    Set-Location bootstrap
    go vet ./...
    Set-Location ..
}

function Clean-All {
    Write-ColorOutput "🧹 Cleaning build artifacts..." "Yellow"
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue **/node_modules
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue **/dist
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue **/__pycache__
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue **/build
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue **/bin
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue **/.pytest_cache
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue **/coverage
}

function Install-Deps {
    Write-ColorOutput "📦 Installing dependencies..." "Green"
    pnpm install
    Set-Location companion
    pnpm install
    Set-Location ../schemas
    pnpm install
    Set-Location ../agent
    pip install -e .
    Set-Location ../executor
    pip install -e .
    Set-Location ../bootstrap
    go mod tidy
    Set-Location ..
}

function Show-Help {
    Write-ColorOutput "Ezra - Universal System Agent" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Available targets:"
    Write-ColorOutput "  build        - Build all components"
    Write-ColorOutput "  lint         - Lint all components"
    Write-ColorOutput "  test         - Test all components"
    Write-ColorOutput "  clean        - Clean build artifacts"
    Write-ColorOutput "  deps         - Install dependencies"
    Write-ColorOutput "  help         - Show this help"
    Write-ColorOutput ""
    Write-ColorOutput "Usage: .\build.ps1 [target]"
}

# Main execution
switch ($Target.ToLower()) {
    "build" {
        Write-ColorOutput "🚀 Building Ezra..." "Green"
        Build-Schemas
        Build-Companion
        Build-Agent
        Build-Executor
        if (Get-Command go -ErrorAction SilentlyContinue) {
            Build-Bootstrap
        } else {
            Write-ColorOutput "⚠️  Go not installed, skipping bootstrap build" "Yellow"
        }
        Write-ColorOutput "✅ All components built successfully" "Green"
    }
    "test" {
        Test-All
        Write-ColorOutput "✅ All tests completed" "Green"
    }
    "lint" {
        Lint-All
        Write-ColorOutput "✅ All linting completed" "Green"
    }
    "clean" {
        Clean-All
        Write-ColorOutput "✅ Clean completed" "Green"
    }
    "deps" {
        Install-Deps
        Write-ColorOutput "✅ Dependencies installed" "Green"
    }
    "help" {
        Show-Help
    }
    default {
        Write-ColorOutput "Unknown target: $Target" "Red"
        Show-Help
    }
}