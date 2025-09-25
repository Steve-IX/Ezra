"""Command-line interface for Ezra agent."""

import sys
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .config import ConfigManager
from .device import DeviceScanner
from .companion_client import CompanionClient

app = typer.Typer(help="Ezra Control CLI - Manage your Ezra agent")
console = Console()


@app.command()
def init(
    companion_url: str = typer.Option("http://localhost:3000", "--companion-url", help="Companion server URL"),
    device_id: Optional[str] = typer.Option(None, "--device-id", help="Device identifier"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
):
    """Initialize agent configuration."""
    config_manager = ConfigManager(config_file)
    
    # Create default config
    config = config_manager._create_default_config()
    config.companion_url = companion_url
    
    if device_id:
        config.device_id = device_id
    
    # Save configuration
    config_manager._config = config
    config_manager.save()
    
    console.print(f"✅ Configuration initialized at {config_manager.config_path}")
    console.print(f"📡 Companion URL: {config.companion_url}")
    console.print(f"🆔 Device ID: {config.device_id}")


@app.command()
def config(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
):
    """Show current configuration."""
    config_manager = ConfigManager(config_file)
    config = config_manager.load()
    
    table = Table(title="Agent Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Companion URL", config.companion_url)
    table.add_row("Device ID", config.device_id)
    table.add_row("Polling Interval", f"{config.polling_interval}ms")
    table.add_row("Max Retries", str(config.max_retries))
    table.add_row("Timeout", f"{config.timeout}ms")
    table.add_row("Log Level", config.log_level)
    table.add_row("Data Directory", str(config.data_dir))
    table.add_row("Cache Directory", str(config.cache_dir))
    table.add_row("Backup Directory", str(config.backup_dir))
    
    console.print(table)


@app.command()
def scan(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
):
    """Scan device information."""
    config_manager = ConfigManager(config_file)
    config = config_manager.load()
    
    scanner = DeviceScanner()
    device_info = scanner.scan(config.device_id)
    
    # Display device information
    console.print(Panel.fit(f"[bold]Device Information[/bold]\n", style="blue"))
    
    table = Table(title="Device Details")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("ID", device_info.id)
    table.add_row("Platform", device_info.platform)
    table.add_row("OS", f"{device_info.os} {device_info.version}")
    table.add_row("Architecture", device_info.architecture)
    table.add_row("CPU", device_info.hardware.cpu)
    table.add_row("Memory", f"{device_info.hardware.memory // (1024**3)} GB")
    table.add_row("Storage", f"{device_info.hardware.storage // (1024**3)} GB")
    if device_info.hardware.gpu:
        table.add_row("GPU", device_info.hardware.gpu)
    
    console.print(table)
    
    # Display capabilities
    if device_info.capabilities:
        console.print("\n[bold]Capabilities:[/bold]")
        for capability in device_info.capabilities:
            console.print(f"  • {capability}")


@app.command()
def test(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
):
    """Test connection to companion server."""
    config_manager = ConfigManager(config_file)
    config = config_manager.load()
    
    client = CompanionClient(config)
    
    console.print("🔍 Testing companion server connection...")
    
    # Health check
    if client.health_check():
        console.print("✅ Companion server is healthy")
    else:
        console.print("❌ Companion server is not available")
        return
    
    # Get providers status
    providers = client.get_providers_status()
    if providers:
        console.print("\n📡 LLM Providers:")
        for provider in providers.get('providers', []):
            status = "✅" if provider.get('available') else "❌"
            console.print(f"  {status} {provider.get('name')}")
    
    # Get public key
    public_key = client.get_public_key()
    if public_key:
        console.print(f"\n🔑 Public Key: {public_key[:32]}...")


@app.command()
def install(
    service: bool = typer.Option(False, "--service", help="Install as system service"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
):
    """Install agent as system service."""
    if not service:
        console.print("Use --service flag to install as system service")
        return
    
    # This would be implemented based on the platform
    console.print("🔧 Installing agent as system service...")
    
    if sys.platform == "linux":
        # Create systemd service file
        service_content = f"""[Unit]
Description=Ezra Agent
After=network.target

[Service]
Type=simple
User=ezra
WorkingDirectory={Path.home() / '.ezra'}
ExecStart=/usr/local/bin/ezra-agent start --daemon
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/etc/systemd/system/ezra-agent.service")
        console.print(f"📝 Creating service file: {service_file}")
        # Note: This would require sudo privileges
        console.print("⚠️  Run with sudo to install system service")
        
    elif sys.platform == "win32":
        # Create Windows service
        console.print("📝 Creating Windows service...")
        console.print("⚠️  Windows service installation not yet implemented")
    
    else:
        console.print("❌ Service installation not supported on this platform")


if __name__ == "__main__":
    app()
