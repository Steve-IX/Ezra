"""Companion server client for communication."""

from typing import Any

import requests
from loguru import logger
from pydantic import BaseModel

from .config import AgentConfig
from .device import DeviceInfo


class AgentRequest(BaseModel):
    """Agent request model."""

    device_info: DeviceInfo
    user_prompt: str
    context: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    """Agent response model."""

    action_plan: dict[str, Any]
    human_readable_summary: str
    consent_required: bool
    estimated_risk: str


class CompanionClient:
    """Client for communicating with companion server."""

    def __init__(self, config: AgentConfig):
        """Initialize companion client."""
        self.config = config
        self.base_url = config.companion_url.rstrip("/")
        self.session = requests.Session()
        self.session.timeout = config.timeout / 1000  # Convert to seconds

        # Set up session headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": f"Ezra-Agent/0.1.0 (Device: {config.device_id})",
        })

    def health_check(self) -> bool:
        """Check if companion server is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False
        else:
            return True

    def generate_action_plan(self, request: AgentRequest) -> AgentResponse | None:
        """Generate action plan from companion server."""
        try:
            url = f"{self.base_url}/api/v1/agent/plan"
            data = request.dict()

            logger.info(f"Sending request to companion server: {url}")
            response = self.session.post(url, json=data)
            response.raise_for_status()

            response_data = response.json()
            return AgentResponse(**response_data)

        except requests.RequestException as e:
            logger.error(f"Failed to generate action plan: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid response from companion server: {e}")
            return None

    def verify_signature(
        self, action_plan: dict[str, Any], signature: dict[str, Any],
    ) -> bool:
        """Verify action plan signature."""
        try:
            url = f"{self.base_url}/api/v1/agent/verify"
            data = {
                "action_plan": action_plan,
                "signature": signature,
            }

            response = self.session.post(url, json=data)
            response.raise_for_status()

            result = response.json()
            return result.get("valid", False)

        except requests.RequestException as e:
            logger.error(f"Failed to verify signature: {e}")
            return False
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid verification response: {e}")
            return False

    def get_public_key(self) -> str | None:
        """Get companion server public key."""
        try:
            url = f"{self.base_url}/api/v1/crypto/public-key"
            response = self.session.get(url)
            response.raise_for_status()

            result = response.json()
            return result.get("public_key")

        except requests.RequestException as e:
            logger.error(f"Failed to get public key: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid public key response: {e}")
            return None

    def get_providers_status(self) -> dict[str, Any] | None:
        """Get LLM providers status."""
        try:
            url = f"{self.base_url}/api/v1/llm/providers"
            response = self.session.get(url)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to get providers status: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid providers response: {e}")
            return None
