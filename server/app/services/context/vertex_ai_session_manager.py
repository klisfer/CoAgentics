"""
Manages interaction with Google Cloud Vertex AI for session and memory services.

This module encapsulates the setup and interaction with Vertex AI's Agent Engine,
including session management and the long-term Memory Bank. It is designed to be
a replacement for the in-memory session manager for production environments.

Reference: https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/quickstart-adk
"""

import os
from typing import Optional

import vertexai
from google.adk.sessions import VertexAiSessionService
from google.adk.memory import VertexAiMemoryBankService

class VertexAIManager:
    """A manager for Vertex AI Agent Engine services."""

    def __init__(self):
        self._initialized = False
        self.project_id: Optional[str] = None
        self.location: Optional[str] = None
        self.agent_engine_id: Optional[str] = None
        self.session_service: Optional[VertexAiSessionService] = None
        self.memory_service: Optional[VertexAiMemoryBankService] = None

    def initialize(
        self,
        project_id: str,
        location: str = "us-central1",
    ):
        """
        Initializes the connection to Vertex AI services.

        This must be called before any other methods are used. It sets up the
        environment variables, initializes the Vertex AI client, and creates or
        gets the necessary services.

        Args:
            project_id: Your Google Cloud project ID.
            location: The Google Cloud location. Defaults to "us-central1".
        """
        if self._initialized:
            return

        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        os.environ["GOOGLE_CLOUD_LOCATION"] = location

        self.project_id = project_id
        self.location = location

        try:
            vertexai.init(project=project_id, location=location)
            client = vertexai.Client(project=project_id, location=location)
            
            # For this example, we create a new ephemeral agent engine instance
            # on each startup. For a real production system, you might want to
            # retrieve an existing one by its ID.
            agent_engine = client.agent_engines.create()
            self.agent_engine_id = agent_engine.api_resource.name.split("/")[-1]

            self.session_service = VertexAiSessionService(
                project=project_id,
                location=location,
                agent_engine_id=self.agent_engine_id,
            )

            self.memory_service = VertexAiMemoryBankService(
                project=project_id,
                location=location,
                agent_engine_id=self.agent_engine_id,
            )
            self._initialized = True
            print("Vertex AI Manager initialized successfully.")
            print(f"Agent Engine ID: {self.agent_engine_id}")

        except Exception as e:
            print(f"Failed to initialize Vertex AI Manager: {e}")
            self._initialized = False
            raise

    def get_session_service(self) -> VertexAiSessionService:
        if not self._initialized or not self.session_service:
            raise RuntimeError("VertexAIManager is not initialized. Call .initialize() first.")
        return self.session_service

    def get_memory_service(self) -> VertexAiMemoryBankService:
        if not self._initialized or not self.memory_service:
            raise RuntimeError("VertexAIManager is not initialized. Call .initialize() first.")
        return self.memory_service

# Global instance of the Vertex AI manager
vertex_ai_manager = VertexAIManager() 