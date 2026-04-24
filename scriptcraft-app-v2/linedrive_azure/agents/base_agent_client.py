#!/usr/bin/env python3
"""
BaseAgentClient (v2 app) - DUAL-MODE Azure AI Agent Client

Supports BOTH:
  - "v1" mode (classic Assistants API via azure-ai-agents AgentsClient).
    Same agent IDs and behavior as scriptcraft-app (the working v1 app).
  - "v2" mode (new Microsoft Foundry Agents experience: Conversations + Responses
    via project.get_openai_client() with agent_reference by NAME).

The active mode is controlled by the env var FOUNDRY_API_MODE ("v1" or "v2"),
which the web GUI sets at runtime via a toggle.

Subclasses do NOT need to change. They keep calling
    super().__init__(agent_id="asst_...", agent_name="...")
and using self.create_thread() / self.send_message(...).
The base class transparently dispatches to the right backend.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from azure.identity import DefaultAzureCredential

# v2 / new Foundry SDK (azure-ai-projects >= 2.0.0)
from azure.ai.projects import AIProjectClient

# Classic Assistants SDK still ships in azure-ai-agents 1.1.0 (separate package)
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ListSortOrder

PROJECT_ENDPOINT = (
    "https://linedrive-ai-foundry.services.ai.azure.com/api/projects/linedriveAgents"
)

# Map v1 agent_name -> v2 (new Foundry) agent_name. Lookup is case-insensitive
# (see _resolve_v2_name). Add entries for any v1 name that does not match the
# corresponding v2 name verbatim, including alternative casings/prefixes used
# by v1 client constructors.
V1_TO_V2_AGENT_NAME: Dict[str, str] = {
    "Script-Review-Agent": "Script-Reviewer-Agent",
    "Script-Quotes-and-Statistics-Agent": "Statistics-and-Quotes-Finder-Agent",
    # YouTube upload (v1 client uses capital T in constructor)
    "Youtube-Upload-Details-Agent": "Script-Youtube-Upload-Details-Agent",
    "YouTube-Upload-Details-Agent": "Script-Youtube-Upload-Details-Agent",
    # Hook-and-Summary (v1 client constructor omits the "Script-" prefix)
    "Hook-and-Summary-Agent": "Script-Hook-and-Summary-Agent",
    "Script-Hook-and-Summary-Agent": "Script-Hook-and-Summary-Agent",
    "Script-Repeat-and-Flow-Agent": "Script-Repeat-and-Flow-Agent",
    "Script-Polisher-Agent": "Script-Polisher-Agent",
    "Script-bRoll-Agent": "Script-bRoll-Agent",
    "Script-Writer-Agent": "Script-Writer-Agent",
    "Script-Topic-Assistant-Agent": "Script-Topic-Assistant-Agent",
    "Script-Demo-Assistant-Agent": "Script-Demo-Assistant-Agent",
}

# Lower-cased lookup for robustness against minor casing differences.
_V1_TO_V2_LOWER: Dict[str, str] = {k.lower(): v for k, v in V1_TO_V2_AGENT_NAME.items()}


def _resolve_v2_name(v1_name: str) -> str:
    """Return the v2 agent name for a given v1 name (case-insensitive). Falls back to the v1 name."""
    if not v1_name:
        return v1_name
    return _V1_TO_V2_LOWER.get(v1_name.lower(), v1_name)


def get_api_mode() -> str:
    """Return 'v1' (default, classic) or 'v2' (new Foundry) based on FOUNDRY_API_MODE env."""
    mode = (os.environ.get("FOUNDRY_API_MODE") or "v1").strip().lower()
    return "v2" if mode == "v2" else "v1"


class BaseAgentClient(ABC):
    """Dual-mode base client. Public surface is unchanged from the v1 app."""

    def __init__(self, agent_id: str, agent_name: str = None):
        self.agent_id = agent_id
        self.agent_name = agent_name or f"Agent-{agent_id}"
        self.v2_agent_name = _resolve_v2_name(self.agent_name)
        self._credential = DefaultAzureCredential()
        # Lazy-init clients so we never touch the v1 SDK if user only uses v2 (and vice-versa)
        self._v1_client: Optional[AgentsClient] = None
        self._v2_project: Optional[AIProjectClient] = None
        self._v2_openai = None
        self._v1_validated = False

    # ------------------------------------------------------------------ helpers
    def _v1(self) -> AgentsClient:
        if self._v1_client is None:
            self._v1_client = AgentsClient(
                endpoint=PROJECT_ENDPOINT, credential=self._credential
            )
        if not self._v1_validated:
            # Retry validation to ride through transient SSL/network blips
            # (e.g. SSL: UNEXPECTED_EOF_WHILE_READING from Azure front door).
            import time as _time
            last_err = None
            for attempt in range(3):
                try:
                    self._v1_client.get_agent(self.agent_id)
                    self._v1_validated = True
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    msg = str(e).lower()
                    transient = (
                        "ssl" in msg
                        or "eof" in msg
                        or "timed out" in msg
                        or "timeout" in msg
                        or "connection" in msg
                        or "reset" in msg
                    )
                    if not transient or attempt == 2:
                        break
                    _time.sleep(1.5 * (attempt + 1))
            if last_err is not None:
                raise Exception(
                    f"Failed to initialize v1 agent {self.agent_id}: {last_err}"
                )
        return self._v1_client

    def _v2(self):
        if self._v2_project is None:
            self._v2_project = AIProjectClient(
                endpoint=PROJECT_ENDPOINT, credential=self._credential
            )
            self._v2_openai = self._v2_project.get_openai_client()
        return self._v2_project, self._v2_openai

    # ------------------------------------------------------------------ public API
    def create_thread(self) -> Optional[Any]:
        """Create a new conversation/thread for the active API mode.
        Returned object exposes an `.id` attribute that callers should pass back to send_message."""
        mode = get_api_mode()
        if mode == "v2":
            import time as _time
            last_err = None
            for attempt in range(3):
                try:
                    _, openai = self._v2()
                    conv = openai.conversations.create()
                    return conv  # has .id
                except Exception as e:
                    last_err = e
                    msg = str(e).lower()
                    transient = (
                        "ssl" in msg
                        or "eof" in msg
                        or "timed out" in msg
                        or "timeout" in msg
                        or "connection" in msg
                        or "reset" in msg
                        or "remote disconnected" in msg
                        or "broken pipe" in msg
                    )
                    if not transient or attempt == 2:
                        break
                    # Force re-init of the openai client on next attempt in case
                    # the underlying httpx session is in a bad state.
                    self._v2_project = None
                    self._v2_openai = None
                    _time.sleep(1.5 * (attempt + 1))
            raise Exception(f"Failed to create v2 conversation: {last_err}")
        # v1
        try:
            return self._v1().threads.create()
        except Exception as e:
            raise Exception(f"Failed to create v1 thread: {e}")

    def send_message(
        self,
        thread_id: str,
        message_content: str,
        show_sources: bool = False,
        timeout: int = 300,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        if get_api_mode() == "v2":
            return self._send_v2(thread_id, message_content, timeout, max_retries)
        return self._send_v1(
            thread_id, message_content, show_sources, timeout, max_retries
        )

    # ------------------------------------------------------------------ v2 backend
    def _send_v2(
        self,
        conversation_id: str,
        message_content: str,
        timeout: int,
        max_retries: int,
    ) -> Dict[str, Any]:
        _, openai = self._v2()
        delay = 5
        last_err: Optional[str] = None

        for attempt in range(max_retries + 1):
            try:
                t0 = time.time()
                print(
                    f"⏱️ [v2] Running {self.v2_agent_name} on conv {conversation_id} (timeout={timeout}s)..."
                )
                response = openai.responses.create(
                    input=message_content,
                    conversation=conversation_id,
                    extra_body={
                        "agent_reference": {
                            "name": self.v2_agent_name,
                            "type": "agent_reference",
                        }
                    },
                    timeout=timeout,
                )
                elapsed = time.time() - t0
                print(f"✅ [v2] {self.v2_agent_name} completed in {elapsed:.1f}s")

                text_parts: List[str] = []
                for item in getattr(response, "output", []) or []:
                    if getattr(item, "type", None) != "message":
                        continue
                    for block in getattr(item, "content", []) or []:
                        txt = getattr(block, "text", None)
                        if isinstance(txt, str) and txt:
                            text_parts.append(txt)
                        elif isinstance(block, dict) and isinstance(
                            block.get("text"), str
                        ):
                            text_parts.append(block["text"])
                response_text = "\n".join(text_parts).strip()

                if not response_text:
                    return {
                        "success": False,
                        "error": "Empty response from v2 agent",
                        "response": None,
                        "sources": [],
                    }
                return {
                    "success": True,
                    "response": response_text,
                    "sources": [],
                    "error": None,
                }

            except Exception as e:
                last_err = str(e)
                low = last_err.lower()
                is_retryable = (
                    "rate" in low
                    or "429" in last_err
                    or "timeout" in low
                    or "timed out" in low
                    or "connection" in low
                    or "ssl" in low
                    or "eof" in low
                    or "reset" in low
                    or "remote disconnected" in low
                    or "broken pipe" in low
                )
                if is_retryable and attempt < max_retries:
                    print(
                        f"⏳ [v2] {last_err[:120]} — retry {attempt+1}/{max_retries} in {delay}s"
                    )
                    # Reset openai client on connection-class errors so we get a fresh session
                    if "connection" in low or "ssl" in low or "eof" in low or "reset" in low:
                        self._v2_project = None
                        self._v2_openai = None
                    time.sleep(delay)
                    delay *= 2
                    continue
                break

        return {
            "success": False,
            "error": last_err or "v2 send failed",
            "response": None,
            "sources": [],
        }

    # ------------------------------------------------------------------ v1 backend (classic Assistants)
    def _send_v1(
        self,
        thread_id: str,
        message_content: str,
        show_sources: bool,
        timeout: int,
        max_retries: int,
    ) -> Dict[str, Any]:
        client = self._v1()

        # Cancel any active runs on the thread first
        try:
            runs = client.runs.list(thread_id=thread_id)
            for run in runs:
                if run.status in ["in_progress", "queued", "requires_action"]:
                    print(
                        f"⚠️ Found active run {run.id} with status {run.status}, cancelling..."
                    )
                    try:
                        client.runs.cancel(thread_id=thread_id, run_id=run.id)
                        print(f"✅ Cancelled active run {run.id}")
                        time.sleep(3)
                    except Exception as cancel_error:
                        print(f"⚠️ Could not cancel run: {cancel_error}")
                        time.sleep(5)
        except Exception as list_error:
            print(f"⚠️ Could not check for active runs: {list_error}")

        retry_count = 0
        base_delay = 5

        while retry_count <= max_retries:
            try:
                if retry_count == 0:
                    client.messages.create(
                        thread_id=thread_id,
                        role="user",
                        content=message_content,
                    )
                else:
                    print(
                        f"🔄 Retry {retry_count}/{max_retries} for {self.agent_name}..."
                    )

                run = None
                try:
                    print(
                        f"⏱️ [v1] Running {self.agent_name} with {timeout}s timeout..."
                    )
                    print(f"📊 Agent: {self.agent_name} (ID: {self.agent_id})")
                    print(f"🧵 Thread ID: {thread_id}")

                    start_time = time.time()
                    last_status_time = start_time

                    run = client.runs.create(
                        thread_id=thread_id,
                        agent_id=self.agent_id,
                        additional_instructions="",
                    )

                    while True:
                        run = client.runs.get(thread_id=thread_id, run_id=run.id)
                        current_time = time.time()

                        if current_time - last_status_time >= 30:
                            elapsed = current_time - start_time
                            print(
                                f"⏳ Status: {run.status} | Elapsed: {int(elapsed)}s | "
                                f"Timeout in: {int(timeout - elapsed)}s"
                            )
                            last_status_time = current_time

                        if run.status in [
                            "completed",
                            "failed",
                            "cancelled",
                            "expired",
                        ]:
                            break

                        if current_time - start_time > timeout:
                            print(f"🛑 Timeout reached! Cancelling run...")
                            try:
                                client.runs.cancel(
                                    thread_id=thread_id, run_id=run.id
                                )
                                print(
                                    f"⏳ Waiting for run {run.id} to finish cancelling..."
                                )
                                for wait_attempt in range(30):
                                    time.sleep(2)
                                    check_run = client.runs.get(
                                        thread_id=thread_id, run_id=run.id
                                    )
                                    print(
                                        f"   Status: {check_run.status} (attempt {wait_attempt + 1}/30)"
                                    )
                                    if check_run.status in [
                                        "cancelled",
                                        "completed",
                                        "failed",
                                        "expired",
                                    ]:
                                        break
                            except Exception as cancel_error:
                                print(f"⚠️ Error during cancellation: {cancel_error}")
                            raise Exception(
                                f"Agent run timed out after {timeout} seconds"
                            )

                        time.sleep(2)

                    elapsed = time.time() - start_time
                    print(f"✅ Agent completed in {elapsed:.1f} seconds")

                except Exception as e:
                    error_str = str(e)
                    if "already has an active run" in error_str:
                        print(f"⚠️ Thread has active run. Attempting cleanup...")
                        try:
                            runs = client.runs.list(thread_id=thread_id)
                            for existing_run in runs:
                                if existing_run.status in [
                                    "in_progress",
                                    "queued",
                                    "requires_action",
                                    "cancelling",
                                ]:
                                    print(
                                        f"🛑 Cancelling conflicting run {existing_run.id}"
                                    )
                                    try:
                                        client.runs.cancel(
                                            thread_id=thread_id,
                                            run_id=existing_run.id,
                                        )
                                    except Exception as cancel_error:
                                        if (
                                            "cancelling"
                                            not in str(cancel_error).lower()
                                        ):
                                            raise
                                    for wait_attempt in range(30):
                                        time.sleep(2)
                                        check_run = client.runs.get(
                                            thread_id=thread_id,
                                            run_id=existing_run.id,
                                        )
                                        if check_run.status in [
                                            "cancelled",
                                            "completed",
                                            "failed",
                                            "expired",
                                        ]:
                                            break
                        except Exception as cleanup_error:
                            print(f"⚠️ Cleanup failed: {cleanup_error}")

                        if retry_count < max_retries:
                            delay = base_delay * (2**retry_count)
                            print(f"⏳ Waiting {delay} seconds before retry...")
                            time.sleep(delay)
                            retry_count += 1
                            continue

                    if run:
                        try:
                            client.runs.cancel(thread_id=thread_id, run_id=run.id)
                            time.sleep(2)
                        except Exception:
                            pass
                    raise e

                if run.status == "failed":
                    error_msg = f"Run failed: {run.last_error}"
                    if "rate" in str(run.last_error).lower() or "429" in str(
                        run.last_error
                    ):
                        if retry_count < max_retries:
                            delay = base_delay * (2**retry_count)
                            print(f"⏳ Rate limit. Waiting {delay}s before retry...")
                            time.sleep(delay)
                            retry_count += 1
                            continue
                    return {
                        "success": False,
                        "error": error_msg,
                        "response": None,
                        "sources": [],
                    }

                messages = client.messages.list(
                    thread_id=thread_id, order=ListSortOrder.ASCENDING
                )
                for message in reversed(list(messages)):
                    if message.role == "assistant" and message.text_messages:
                        response_text = message.text_messages[-1].text.value
                        sources = (
                            self._extract_sources(message) if show_sources else []
                        )
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
                low = error_str.lower()
                is_rate_limit = "rate" in low or "429" in error_str
                is_timeout = "timeout" in low or "timed out" in low
                if (is_rate_limit or is_timeout) and retry_count < max_retries:
                    delay = base_delay * (2**retry_count)
                    err_type = "Rate limit" if is_rate_limit else "Timeout"
                    print(
                        f"⏳ {err_type} detected. Waiting {delay}s before retry "
                        f"{retry_count + 1}/{max_retries}..."
                    )
                    time.sleep(delay)
                    retry_count += 1
                    continue
                return {
                    "success": False,
                    "error": (
                        f"{error_str} (after {retry_count} retries)"
                        if retry_count > 0
                        else error_str
                    ),
                    "response": None,
                    "sources": [],
                }

        return {
            "success": False,
            "error": f"Max retries ({max_retries}) exceeded for {self.agent_name}",
            "response": None,
            "sources": [],
        }

    # ------------------------------------------------------------------ misc
    def _extract_sources(self, message) -> List[Dict[str, Any]]:
        sources: List[Dict[str, Any]] = []
        try:
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
        except Exception:
            pass
        return sources

    def get_agent_info(self) -> Dict[str, str]:
        return {
            "name": self.agent_name,
            "v2_name": self.v2_agent_name,
            "id": self.agent_id,
            "endpoint": PROJECT_ENDPOINT,
            "api_mode": get_api_mode(),
        }

    @abstractmethod
    def get_specialized_info(self) -> Dict[str, Any]:
        """Subclasses provide a description of their specialty."""

    def health_check(self) -> Dict[str, Any]:
        try:
            agent_info = self.get_agent_info()
            self.create_thread()
            return {
                "success": True,
                "agent_info": agent_info,
                "thread_creation": "OK",
                "status": f"Healthy ({get_api_mode()})",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "status": "Unhealthy"}


# Compat shim: legacy callers use `self.project.agents.threads.create()` etc.
# In the new SDK AIProjectClient no longer has a `.agents` attr, so we wrap the
# AgentsClient and expose itself as `.agents` so all old call patterns keep
# working in v1 mode (project.agents.threads / messages / runs / get_agent).
# IMPORTANT: in v2 mode `.threads.create()` must return a Foundry conversation,
# not a v1 thread, so we intercept that one call and dispatch via the owning
# BaseAgentClient.create_thread().
class _ThreadsShim:
    def __init__(self, owner):
        self._owner = owner  # BaseAgentClient

    def create(self, *args, **kwargs):
        # Mode-aware: returns v1 thread or v2 conversation as appropriate.
        return self._owner.create_thread()

    def __getattr__(self, name):
        # Any other thread op falls through to the v1 ThreadsOperations
        # (delete/get/list/update). Only meaningful in v1 mode.
        return getattr(self._owner._v1().threads, name)


class _LegacyAgentsShim:
    def __init__(self, owner):
        self._owner = owner
        self._agents_client = owner._v1()
        self._threads_shim = _ThreadsShim(owner)

    @property
    def threads(self):
        return self._threads_shim

    def __getattr__(self, name):
        # messages / runs / get_agent / etc. → real v1 AgentsClient
        return getattr(self._agents_client, name)


class _LegacyProjectShim:
    def __init__(self, owner):
        self._owner = owner
        self._agents_shim = _LegacyAgentsShim(owner)

    @property
    def agents(self):
        return self._agents_shim

    def __getattr__(self, name):
        # Fall through to AgentsClient for any other attribute access
        return getattr(self._owner._v1(), name)


def _legacy_project_property(self):
    return _LegacyProjectShim(self)


BaseAgentClient.project = property(_legacy_project_property)  # type: ignore[attr-defined]
