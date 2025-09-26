"""Main agent daemon application."""

import asyncio
import signal
import sys
from pathlib import Path

import typer
from loguru import logger

from .companion_client import AgentRequest, CompanionClient
from .config import AgentConfig, ConfigManager
from .device import DeviceScanner
from .executor import ActionExecutor

# Default options to avoid B008 errors
_CONFIG_OPTION = typer.Option(
    None, "--config", "-c", help="Configuration file path",
)


class AgentDaemon:
    """Main agent daemon class."""

    def __init__(self, config: AgentConfig):
        """Initialize agent daemon."""
        self.config = config
        self.device_scanner = DeviceScanner()
        self.companion_client = CompanionClient(config)
        self.executor = ActionExecutor(config)
        self.running = False
        self.device_info = None

    async def start(self) -> None:
        """Start the agent daemon."""
        logger.info("Starting Ezra Agent Daemon")

        # Scan device information
        self.device_info = self.device_scanner.scan(self.config.device_id)
        logger.info(
            f"Device scanned: {self.device_info.platform} {self.device_info.os}",
        )

        # Check companion server health
        if not self.companion_client.health_check():
            logger.error("Companion server is not available")
            return

        logger.info("Companion server is healthy")
        self.running = True

        # Start main loop
        await self._main_loop()

    async def stop(self) -> None:
        """Stop the agent daemon."""
        logger.info("Stopping Ezra Agent Daemon")
        self.running = False

    async def _main_loop(self) -> None:
        """Main agent loop."""
        while self.running:
            try:
                # Check for new requests (polling)
                # In a real implementation, this would be more sophisticated
                await asyncio.sleep(self.config.polling_interval / 1000)

                # For now, just log status
                if self.running:
                    logger.debug("Agent is running and healthy")

            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except (ValueError, RuntimeError, ConnectionError) as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def process_request(
        self, user_prompt: str, context: dict | None = None,
    ) -> bool:
        """Process a user request."""
        try:
            # Create agent request
            request = AgentRequest(
                device_info=self.device_info,
                user_prompt=user_prompt,
                context=context,
            )

            # Generate action plan
            response = self.companion_client.generate_action_plan(request)
            if not response:
                logger.error("Failed to generate action plan")
                return False

            # Verify signature
            if not self.companion_client.verify_signature(
                response.action_plan,
                response.action_plan.get("signature", {}),
            ):
                logger.error("Action plan signature verification failed")
                return False

            # Show human-readable summary
            logger.info(f"Action Plan Summary: {response.human_readable_summary}")
            logger.info(f"Risk Level: {response.estimated_risk}")
            logger.info(f"Consent Required: {response.consent_required}")

            # For now, auto-approve if no consent required
            if response.consent_required:
                logger.warning("Consent required - manual approval needed")
                return False

            # Execute action plan
            results = self.executor.execute_action_plan(response.action_plan)

            # Log results and check for failures
            failed_actions = []
            for result in results:
                if result.status == "completed":
                    logger.info(f"Action {result.action_id} completed successfully")
                else:
                    logger.error(f"Action {result.action_id} failed: {result.error}")
                    failed_actions.append(result.action_id)
            else:
                return not failed_actions

        except (ValueError, RuntimeError, ConnectionError) as e:
            logger.error(f"Error processing request: {e}")
            return False


# CLI Application
app = typer.Typer(help="Ezra Agent - Universal system agent daemon")


@app.command()
def start(
    config_file: Path | None = _CONFIG_OPTION,
    daemon: bool = typer.Option(False, "--daemon", "-d", help="Run as daemon"),
):
    """Start the agent daemon."""
    # Load configuration
    config_manager = ConfigManager(config_file)
    config = config_manager.load()

    # Set up logging
    logger.remove()
    logger.add(
        sys.stderr,
        level=config.log_level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )

    if daemon:
        # Set up daemon logging
        log_file = config.data_dir / "agent.log"
        logger.add(
            log_file,
            level=config.log_level.upper(),
            rotation="10 MB",
            retention="7 days",
        )

    # Create and start daemon
    daemon = AgentDaemon(config)

    # Set up signal handlers
    def signal_handler(signum, _frame):
        logger.info(f"Received signal {signum}")
        task = asyncio.create_task(daemon.stop())
        # Store task reference to prevent garbage collection
        signal_handler.task_ref = task

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run daemon
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except (ValueError, RuntimeError, ConnectionError) as e:
        logger.error(f"Agent failed: {e}")
        sys.exit(1)


@app.command()
def request(
    prompt: str = typer.Argument(..., help="User request prompt"),
    config_file: Path | None = _CONFIG_OPTION,
):
    """Process a single request."""
    # Load configuration
    config_manager = ConfigManager(config_file)
    config = config_manager.load()

    # Set up logging
    logger.remove()
    logger.add(
        sys.stderr,
        level=config.log_level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )

    # Create daemon and process request
    daemon = AgentDaemon(config)

    async def process():
        await daemon.start()
        success = await daemon.process_request(prompt)
        await daemon.stop()
        return success

    try:
        success = asyncio.run(process())
        if success:
            logger.info("Request processed successfully")
        else:
            logger.error("Request processing failed")
            sys.exit(1)
    except (ValueError, RuntimeError, ConnectionError) as e:
        logger.error(f"Request failed: {e}")
        sys.exit(1)


@app.command()
def status(
    config_file: Path | None = _CONFIG_OPTION,
):
    """Check agent status."""
    # Load configuration
    config_manager = ConfigManager(config_file)
    config = config_manager.load()

    # Check companion server
    client = CompanionClient(config)
    if client.health_check():
        typer.echo("✅ Companion server is healthy")
    else:
        typer.echo("❌ Companion server is not available")
        return

    # Get providers status
    providers = client.get_providers_status()
    if providers:
        typer.echo("\n📡 LLM Providers:")
        for provider in providers.get("providers", []):
            status = "✅" if provider.get("available") else "❌"
            typer.echo(f"  {status} {provider.get('name')}")

    # Get device info
    scanner = DeviceScanner()
    device_info = scanner.scan(config.device_id)
    typer.echo(
        f"\n🖥️  Device: {device_info.platform} {device_info.os} {device_info.version}",
    )
    typer.echo(f"🏗️  Architecture: {device_info.architecture}")
    typer.echo(f"💾 Memory: {device_info.hardware.memory // (1024**3)} GB")
    typer.echo(f"💿 Storage: {device_info.hardware.storage // (1024**3)} GB")


if __name__ == "__main__":
    app()
