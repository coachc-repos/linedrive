#!/usr/bin/env python3
"""
BaseAgentClient - Generic Azure AI Agent Client

This module provides a base client class for interacting with Azure AI Agents
in the linedrive project. All specific agents inherit from this base class.
"""

import time
import os
from typing import Optional, Dict, Any, List
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
from abc import ABC, abstractmethod


class BaseAgentClient(ABC):
    """Base client for Azure AI Agent interactions"""

    def __init__(self, agent_id: str, agent_name: str = None):
        """
        Initialize the AI Agent connection

        Args:
            agent_id: The Azure AI Agent ID
            agent_name: Optional display name for the agent
        """
        self.project = AIProjectClient(
            credential=DefaultAzureCredential(),
            api_key=os.environ.get("AI_PROJECT_API_KEY"),
            endpoint="https://linedrive-ai-foundry.services.ai.azure.com/api/projects/linedriveAgents",
        )

        try:
            # Get the specific agent by ID
            self.agent = self.project.agents.get_agent(agent_id)
            self.agent_id = agent_id
            self.agent_name = agent_name or getattr(
                self.agent, "name", f"Agent-{agent_id}"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize agent {agent_id}: {e}")

    def create_thread(self) -> Optional[Any]:
        """Create a new conversation thread"""
        try:
            thread = self.project.agents.threads.create()
            return thread
        except Exception as e:
            raise Exception(f"Failed to create thread: {e}")

    def send_message(
        self,
        thread_id: str,
        message_content: str,
        show_sources: bool = False,
        timeout: int = 300,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Send a message to the agent and get response with retry logic

        Args:
            thread_id: The conversation thread ID
            message_content: The user's message
            show_sources: Whether to include source information in response
            timeout: Maximum time to wait for response (seconds)
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Dictionary with 'success', 'response', 'sources', and 'error' keys
        """
        # Check for any active runs on this thread and cancel them
        try:
            runs = self.project.agents.runs.list(thread_id=thread_id)
            for run in runs:
                if run.status in ["in_progress", "queued", "requires_action"]:
                    print(
                        f"⚠️ Found active run {run.id} with status {run.status}, cancelling...")
                    try:
                        self.project.agents.runs.cancel(
                            thread_id=thread_id, run_id=run.id)
                        print(f"✅ Cancelled active run {run.id}")
                        # Wait longer for cancellation to take effect
                        time.sleep(3)
                    except Exception as cancel_error:
                        print(f"⚠️ Could not cancel run: {cancel_error}")
                        # If we can't cancel, wait a bit and hope it completes
                        time.sleep(5)
        except Exception as list_error:
            print(f"⚠️ Could not check for active runs: {list_error}")

        retry_count = 0
        base_delay = 5  # Start with 5 second delay

        while retry_count <= max_retries:
            try:
                # Send user message
                if retry_count == 0:
                    message = self.project.agents.messages.create(
                        thread_id=thread_id, role="user", content=message_content
                    )
                else:
                    # Message already sent, just retry the run
                    print(
                        f"🔄 Retry {retry_count}/{max_retries} for {self.agent_name}...")

                # Process the run with native Azure SDK timeout
                # Note: signal-based timeouts don't work in Flask worker threads
                run = None
                try:
                    print(
                        f"⏱️ Running {self.agent_name} with {timeout}s timeout...")
                    print(f"📊 Agent: {self.agent_name} (ID: {self.agent.id})")
                    print(f"🧵 Thread ID: {thread_id}")
                    print(f"⏳ This may take 1-3 minutes for large scripts...")

                    start_time = time.time()
                    last_status_time = start_time

                    # Create the run (non-blocking)
                    # Note: Pass empty dict for additional_instructions to ensure
                    # agent uses its configured tools (including grounding)
                    run = self.project.agents.runs.create(
                        thread_id=thread_id,
                        agent_id=self.agent.id,
                        additional_instructions=""
                    )

                    # Poll for completion with progress updates
                    while True:
                        run = self.project.agents.runs.get(
                            thread_id=thread_id, run_id=run.id)
                        current_time = time.time()

                        # Show progress every 30 seconds with detailed status
                        if current_time - last_status_time >= 30:
                            elapsed = current_time - start_time
                            print(
                                f"⏳ Status: {run.status} | Elapsed: {int(elapsed)}s | Timeout in: {int(timeout - elapsed)}s")
                            last_status_time = current_time

                        # Check for completion
                        if run.status in ["completed", "failed", "cancelled", "expired"]:
                            break

                        # Check timeout
                        if current_time - start_time > timeout:
                            print(f"🛑 Timeout reached! Cancelling run...")
                            try:
                                self.project.agents.runs.cancel(
                                    thread_id=thread_id, run_id=run.id)

                                # CRITICAL: Wait for cancellation to complete
                                print(
                                    f"⏳ Waiting for run {run.id} to finish cancelling...")
                                # 60 seconds max (Azure can be slow)
                                for wait_attempt in range(30):
                                    time.sleep(2)
                                    check_run = self.project.agents.runs.get(
                                        thread_id=thread_id, run_id=run.id)
                                    print(
                                        f"   Status: {check_run.status} (attempt {wait_attempt + 1}/30)")
                                    if check_run.status in ["cancelled", "completed", "failed", "expired"]:
                                        print(
                                            f"✅ Run {run.id} finished: {check_run.status}")
                                        break
                                else:
                                    print(
                                        f"⚠️ Run {run.id} still not finished after 60 seconds")
                            except Exception as cancel_error:
                                print(
                                    f"⚠️ Error during cancellation: {cancel_error}")
                            raise Exception(
                                f"Agent run timed out after {timeout} seconds")

                        # Wait before next poll
                        time.sleep(2)

                    elapsed = time.time() - start_time
                    print(f"✅ Agent completed in {elapsed:.1f} seconds")

                except Exception as e:
                    error_str = str(e)

                    # Check for "already has an active run" error
                    if "already has an active run" in error_str:
                        print(f"⚠️ Thread has active run. Attempting cleanup...")
                        try:
                            # List all runs and try to cancel active ones
                            runs = self.project.agents.runs.list(
                                thread_id=thread_id)
                            for existing_run in runs:
                                if existing_run.status in ["in_progress", "queued", "requires_action", "cancelling"]:
                                    print(
                                        f"🛑 Cancelling conflicting run {existing_run.id} (status: {existing_run.status})")

                                    # Try to cancel (might already be cancelling)
                                    try:
                                        self.project.agents.runs.cancel(
                                            thread_id=thread_id, run_id=existing_run.id)
                                    except Exception as cancel_error:
                                        # Already cancelling is OK
                                        if "cancelling" not in str(cancel_error).lower():
                                            raise

                                    # Wait for cancellation to complete (up to 60 seconds)
                                    print(
                                        f"⏳ Waiting for run {existing_run.id} to finish cancelling...")
                                    # 30 attempts x 2 seconds = 60 seconds
                                    for wait_attempt in range(30):
                                        time.sleep(2)
                                        check_run = self.project.agents.runs.get(
                                            thread_id=thread_id, run_id=existing_run.id)
                                        print(
                                            f"   Status: {check_run.status} (attempt {wait_attempt + 1}/30)")
                                        if check_run.status in ["cancelled", "completed", "failed", "expired"]:
                                            print(
                                                f"✅ Run {existing_run.id} finished: {check_run.status}")
                                            break
                                    else:
                                        print(
                                            f"⚠️ Run {existing_run.id} still not finished after 60 seconds")

                        except Exception as cleanup_error:
                            print(f"⚠️ Cleanup failed: {cleanup_error}")

                        # If we have retries left, try again
                        if retry_count < max_retries:
                            delay = base_delay * (2 ** retry_count)
                            print(f"⏳ Waiting {delay} seconds before retry...")
                            time.sleep(delay)
                            retry_count += 1
                            continue

                    # Try to cancel the run if it was created
                    if run:
                        try:
                            print(f"🛑 Cancelling failed run...")
                            self.project.agents.runs.cancel(
                                thread_id=thread_id, run_id=run.id)
                            time.sleep(2)
                        except:
                            pass  # Best effort cleanup
                    raise e

                if run.status == "failed":
                    error_msg = f"Run failed: {run.last_error}"

                    # Check if it's a rate limit error
                    if "rate" in str(run.last_error).lower() or "429" in str(run.last_error):
                        if retry_count < max_retries:
                            delay = base_delay * (2 ** retry_count)
                            print(
                                f"⏳ Rate limit detected. Waiting {delay} seconds before retry...")
                            time.sleep(delay)
                            retry_count += 1
                            continue

                    return {
                        "success": False,
                        "error": error_msg,
                        "response": None,
                        "sources": [],
                    }

                # Get all messages and return the latest agent response
                messages = self.project.agents.messages.list(
                    thread_id=thread_id, order=ListSortOrder.ASCENDING
                )

                # Find the latest assistant message
                for message in reversed(list(messages)):
                    if message.role == "assistant" and message.text_messages:
                        response_text = message.text_messages[-1].text.value
                        sources = self._extract_sources(
                            message) if show_sources else []

                        if retry_count > 0:
                            print(f"✅ Retry successful for {self.agent_name}")

                        return {
                            "success": True,
                            "response": response_text,
                            "sources": sources,
                            "error": None,
                        }

                return {
                    "success": False,
                    "error": f"No response from {self.agent_name}",
                    "response": None,
                    "sources": [],
                }

            except Exception as e:
                error_str = str(e)

                # Check if it's a rate limit or timeout error
                is_rate_limit = "rate" in error_str.lower() or "429" in error_str
                is_timeout = "timeout" in error_str.lower() or "timed out" in error_str.lower()

                if (is_rate_limit or is_timeout) and retry_count < max_retries:
                    delay = base_delay * (2 ** retry_count)
                    error_type = "Rate limit" if is_rate_limit else "Timeout"
                    print(
                        f"⏳ {error_type} detected. Waiting {delay} seconds before retry {retry_count + 1}/{max_retries}...")
                    time.sleep(delay)
                    retry_count += 1
                    continue

                # Not retryable or max retries exceeded
                return {
                    "success": False,
                    "error": f"{error_str} (after {retry_count} retries)" if retry_count > 0 else error_str,
                    "response": None,
                    "sources": []
                }

        # Max retries exceeded
        return {
            "success": False,
            "error": f"Max retries ({max_retries}) exceeded for {self.agent_name}",
            "response": None,
            "sources": [],
        }

    def _extract_sources(self, message) -> List[Dict[str, Any]]:
        """Extract source information from message (if available)"""
        sources = []
        try:
            # Extract sources if available in the message
            if hasattr(message, "attachments") and message.attachments:
                for attachment in message.attachments:
                    if hasattr(attachment, "file_citation"):
                        sources.append(
                            {
                                "type": "file_citation",
                                "content": getattr(
                                    attachment.file_citation, "quote", ""
                                ),
                                "file_id": getattr(
                                    attachment.file_citation, "file_id", ""
                                ),
                            }
                        )
        except Exception as e:
            # Sources extraction is optional, don't fail the entire response
            pass
        return sources

    def get_agent_info(self) -> Dict[str, str]:
        """Get basic information about the agent"""
        return {
            "name": self.agent_name,
            "id": self.agent_id,
            "endpoint": "https://linedrive-ai-foundry.services.ai.azure.com/api/projects/linedriveAgents",
        }

    @abstractmethod
    def get_specialized_info(self) -> Dict[str, Any]:
        """Get specialized information about this agent type - must be implemented by subclasses"""
        pass

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the agent"""
        try:
            # Try to get agent details
            agent_info = self.get_agent_info()

            # Try to create a test thread
            test_thread = self.create_thread()

            return {
                "success": True,
                "agent_info": agent_info,
                "thread_creation": "OK",
                "status": "Healthy",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "status": "Unhealthy"}
