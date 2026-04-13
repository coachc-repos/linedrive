#!/usr/bin/env python3
"""
Cloud Cost CLI Assistant
A command-line conversational AI for cloud cost optimization
"""

import argparse
import subprocess
import json
import openai
import os
from datetime import datetime
import sys


class CloudCostCLI:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.conversation_history = []

    def execute_command(self, command, shell_type="bash"):
        """Execute shell command safely"""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=60
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "command": command,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": command}

    def chat_loop(self):
        """Start interactive chat session"""
        print("🌩️  Cloud Cost Assistant")
        print("=" * 50)
        print("Ask me anything about Azure or GCP costs!")
        print("Type 'quit', 'exit', or Ctrl+C to exit")
        print("=" * 50)

        system_prompt = """
You are an expert cloud cost optimization assistant. You help users:
1. Analyze Azure and GCP resources and costs
2. Identify optimization opportunities
3. Execute CLI commands to gather data and make changes
4. Provide practical recommendations

You can execute Azure CLI (az) and Google Cloud CLI (gcloud) commands.
Be conversational, helpful, and focus on actionable cost savings.

When you need to run commands, use the execute_command function.
Always explain what you're doing and why.
"""

        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("\n👋 Goodbye! Hope I helped save you some money!")
                    break

                if not user_input:
                    continue

                print("\n🤖 Assistant: ", end="", flush=True)

                # Prepare messages
                messages = [{"role": "system", "content": system_prompt}]
                messages.extend(self.conversation_history)
                messages.append({"role": "user", "content": user_input})

                # Get AI response with function calling
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    functions=[
                        {
                            "name": "execute_command",
                            "description": "Execute shell command (Azure CLI, GCP CLI, etc.)",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "command": {
                                        "type": "string",
                                        "description": "Command to execute",
                                    },
                                    "explanation": {
                                        "type": "string",
                                        "description": "Brief explanation of what this command does",
                                    },
                                },
                                "required": ["command", "explanation"],
                            },
                        }
                    ],
                    function_call="auto",
                    temperature=0.7,
                )

                message = response.choices[0].message

                # Handle function calls
                if message.get("function_call"):
                    function_args = json.loads(message["function_call"]["arguments"])
                    command = function_args["command"]
                    explanation = function_args.get("explanation", "")

                    print(f"Let me {explanation.lower()}...")
                    print(f"Running: `{command}`")

                    # Execute command
                    result = self.execute_command(command)

                    if result["success"]:
                        print("✅ Command completed successfully!")
                        if result["output"]:
                            print(f"Output:\n{result['output']}")
                    else:
                        print(f"❌ Command failed: {result['error']}")

                    # Send result back to AI for interpretation
                    messages.append(message)
                    messages.append(
                        {
                            "role": "function",
                            "name": "execute_command",
                            "content": json.dumps(result),
                        }
                    )

                    # Get final interpretation
                    final_response = openai.ChatCompletion.create(
                        model="gpt-4", messages=messages, temperature=0.7
                    )

                    print(
                        f"\n📊 Analysis: {final_response.choices[0].message['content']}"
                    )

                else:
                    # Regular response without function call
                    print(message["content"])

                # Update conversation history
                self.conversation_history.append(
                    {"role": "user", "content": user_input}
                )
                self.conversation_history.append(
                    {"role": "assistant", "content": message.get("content", "")}
                )

                # Keep history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue


def main():
    parser = argparse.ArgumentParser(description="Cloud Cost Assistant CLI")
    parser.add_argument(
        "--api-key", help="OpenAI API key", default=os.getenv("OPENAI_API_KEY")
    )
    parser.add_argument("--one-shot", help="Single question mode", action="store_true")
    parser.add_argument(
        "question", nargs="*", help="Question to ask (for one-shot mode)"
    )

    args = parser.parse_args()

    if not args.api_key:
        print("❌ Error: OpenAI API key required")
        print("Set OPENAI_API_KEY environment variable or use --api-key flag")
        sys.exit(1)

    assistant = CloudCostCLI(args.api_key)

    if args.one_shot and args.question:
        # Single question mode
        question = " ".join(args.question)
        print(f"🌩️  Cloud Cost Assistant - One Shot Mode")
        print(f"Question: {question}")
        print("=" * 50)
        # Implementation for one-shot mode would go here
    else:
        # Interactive mode
        assistant.chat_loop()


if __name__ == "__main__":
    main()
