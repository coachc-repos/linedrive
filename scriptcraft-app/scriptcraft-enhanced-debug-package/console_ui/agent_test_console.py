#!/usr/bin/env python3
"""
Agent Test Console
Interactive console to test agents including the OpenAI demo agent.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Ensure project root is on path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from linedrive_azure.agents.openai_demo_agent_client import OpenAIDemoAgentClient
except Exception:
    OpenAIDemoAgentClient = None


class AgentTestConsole:
    def __init__(self):
        self.agents = {}
        self._initialize_agents()

    def _safe_input(self, prompt: str) -> str:
        """Handle input with EOF protection for non-interactive use."""
        try:
            return input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Detected non-interactive mode or interrupt. Exiting...")
            raise SystemExit(0)

    def _safe_input_continue(
        self, prompt: str = "\n⏎ Press Enter to continue..."
    ) -> None:
        """Handle continue prompts with EOF protection."""
        try:
            input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Continuing...")
            return

    def _initialize_agents(self):
        # Initialize demo agent if available
        try:
            if OpenAIDemoAgentClient is not None:
                try:
                    self.agents["demo"] = OpenAIDemoAgentClient()
                    print("✅ Demo agent initialized")
                except Exception as e:
                    # likely missing API key in environment; offer to set and save one
                    print(f"⚠️ Demo agent not initialized: {e}")
                    resp = input(
                        "Would you like to set the demo agent API key now and save it to linedrive_azure/agents/.env? (y/N): "
                    ).strip()
                    if resp.lower() == "y":
                        key = input(
                            "Enter AZURE_OPENAI_DEMO_KEY or OPENAI_API_KEY: "
                        ).strip()
                        if key:
                            try:
                                client = OpenAIDemoAgentClient(api_key=key)
                                saved = False
                                try:
                                    saved = client.save_api_key(key)
                                except Exception:
                                    saved = False
                                if saved:
                                    print("✅ API key saved to agents .env")
                                else:
                                    print(
                                        "⚠️ Could not save API key to .env (check permissions)"
                                    )
                                self.agents["demo"] = client
                            except Exception as ex:
                                print(
                                    f"❌ Failed to initialize demo client with provided key: {ex}"
                                )
                                self.agents["demo"] = None
                        else:
                            print("⚠️ No key entered. Demo agent will not be available.")
                            self.agents["demo"] = None
                    else:
                        self.agents["demo"] = None
            else:
                self.agents["demo"] = None
                print("⚠️ Demo agent class not available (module import failed)")
        except Exception as e:
            self.agents["demo"] = None
            print(f"⚠️ Demo agent not initialized: {e}")

    def run(self):
        while True:
            print("\n🧪 AGENT TEST CONSOLE")
            print("=" * 50)
            print(
                "1. 🧾 Demo Agent — Generate Developer + Everyday Viewer demos from script"
            )
            print("0. Exit")
            print("=" * 50)

            choice = self._safe_input("\nSelect option (0-1): ").strip()

            if choice == "0":
                print("\n👋 Exiting Agent Test Console")
                break
            elif choice == "1":
                self.test_demo_agent()
            else:
                print("❌ Invalid choice. Please select 0 or 1.")

    def split_demo_sections(self, text: str) -> tuple[str, str]:
        """Attempt to split the model output into Developer and Everyday sections.

        The model is instructed to return two clearly separated sections. This helper
        searches for common markers (case-insensitive) and splits the text. If no
        clear split is found it places the full text into the Developer section and
        leaves the Everyday section empty.
        """
        if not text:
            return "", ""

        s_lower = text.lower()

        # Common markers to identify the start of the Everyday Viewer section
        everyday_markers = [
            "everyday viewer demos",
            "everyday viewer demo",
            "everyday viewer",
            "everyday-viewer",
            "everyday demo",
            "everyday",
            "everyday viewer demos",
            "2. everyday-viewer demo package",
            "2. everyday-viewer demo",
            "2. everyday-viewer",
            "everyday-viewer demos",
        ]

        idx = -1
        for m in everyday_markers:
            i = s_lower.find(m)
            if i != -1:
                idx = i
                break

        if idx != -1:
            dev = text[:idx].strip()
            everyday = text[idx:].strip()
            return dev, everyday

        # If we couldn't find an everyday marker, try to find where the Developer section likely ends
        dev_markers = [
            "developer demos",
            "developer demo",
            "developer-focused demo",
            "developer demos",
            "1. developer",
        ]

        # If we find a developer marker but no everyday marker, attempt a conservative split: everything up to first large heading or '2.'
        for m in dev_markers:
            i = s_lower.find(m)
            if i != -1:
                # try to find next numbered section like '\n2'
                j = s_lower.find("\n2", i)
                if j != -1:
                    return text[:j].strip(), text[j:].strip()

        # Final fallback: return the whole text as developer content and empty everyday content
        return text.strip(), ""

    def test_demo_agent(self):
        """Generate demo packages (developer + everyday viewer) via the OpenAI demo agent

        Saves two separate markdown files under `output/` and generates a small docs
        folder under `docs/demo_packages_<timestamp>/` with `developer.md`,
        `everyday.md`, and `index.md` that links them.
        """
        agent = self.agents.get("demo")
        if not agent:
            print("❌ Demo agent not available (check AZURE_OPENAI_DEMO_KEY env var)")
            input("⏎ Press Enter to continue...")
            return

        print("\n🧾 DEMO AGENT - Generate Demo Packages")
        print("=" * 50)
        choice = self._safe_input(
            "Provide path to final script file or press Enter to paste the script: "
        ).strip()
        script_text = ""

        if choice and Path(choice).exists():
            try:
                with open(choice, "r", encoding="utf-8") as f:
                    script_text = f.read()
            except Exception as e:
                print(f"❌ Could not read file: {e}")
                self._safe_input_continue("⏎ Press Enter to continue...")
                return
        else:
            print("\nPaste the script below. End with a blank line.")
            lines = []
            while True:
                try:
                    line = self._safe_input("")
                except EOFError:
                    break
                if line.strip() == "":
                    break
                lines.append(line)
            script_text = "\n".join(lines).strip()

        if not script_text:
            print("❌ No script text provided. Aborting.")
            self._safe_input_continue("⏎ Press Enter to continue...")
            return

        print("📣 Sending script to demo agent (this may take a minute)...")
        result = agent.generate_demo_packages(script_text, max_tokens=8000)

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            print(f"❌ Demo generation failed: {error_msg}")

            # Special handling for reasoning model issues
            if "reasoning model" in error_msg.lower():
                print("\n💡 This appears to be a reasoning model issue. Suggestions:")
                print(
                    "   - Reasoning models (like gpt-5-mini) use tokens for internal thinking"
                )
                print(
                    "   - Try increasing max_tokens further or simplifying the prompt"
                )
                print("   - Consider using a different model if available")

            self._safe_input_continue("⏎ Press Enter to continue...")
            return

        demo_text = result.get("response", "").strip()
        print("\n✅ Demo packages generated. Preview:")
        print("-" * 50)
        # limit preview size in console
        preview = demo_text[:8000]
        print(preview)

        # Try to split into Developer and Everyday sections
        dev_text, everyday_text = self.split_demo_sections(demo_text)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path("output")
        out_dir.mkdir(parents=True, exist_ok=True)

        dev_md = out_dir / f"demo_packages_{ts}_developer.md"
        everyday_md = out_dir / f"demo_packages_{ts}_everyday.md"

        try:
            # Save developer section
            with open(dev_md, "w", encoding="utf-8") as f:
                f.write(dev_text or demo_text)

            # Save everyday section (if present)
            with open(everyday_md, "w", encoding="utf-8") as f:
                if everyday_text:
                    f.write(everyday_text)
                else:
                    f.write(
                        "<!-- Everyday Viewer section not found in model output -->\n\n"
                        + demo_text
                    )

            print(f"\n💾 Saved Developer demo to: {dev_md}")
            print(f"💾 Saved Everyday Viewer demo to: {everyday_md}")

        except Exception as e:
            print(f"❌ Failed to save output files: {e}")

        # Create docs folder with separate files and an index
        try:
            docs_dir = Path("docs") / f"demo_packages_{ts}"
            docs_dir.mkdir(parents=True, exist_ok=True)

            dev_doc = docs_dir / "developer.md"
            everyday_doc = docs_dir / "everyday.md"
            index_doc = docs_dir / "index.md"

            with open(dev_doc, "w", encoding="utf-8") as f:
                f.write("# Developer Demos\n\n")
                f.write(dev_text or demo_text)

            with open(everyday_doc, "w", encoding="utf-8") as f:
                f.write("# Everyday Viewer Demos\n\n")
                if everyday_text:
                    f.write(everyday_text)
                else:
                    f.write(
                        "<!-- Everyday Viewer section not found in model output -->\n\n"
                    )
                    f.write(demo_text)

            with open(index_doc, "w", encoding="utf-8") as f:
                f.write(f"# Demo Packages\n\nGenerated: {ts}\n\n")
                f.write("- [Developer Demos](developer.md)\n")
                f.write("- [Everyday Viewer Demos](everyday.md)\n")

            print(f"\n📚 Generated docs: {docs_dir}/index.md")

        except Exception as e:
            print(f"❌ Failed to create docs: {e}")

        try:
            input("\n⏎ Press Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Exiting...")
            return


if __name__ == "__main__":
    AgentTestConsole().run()
