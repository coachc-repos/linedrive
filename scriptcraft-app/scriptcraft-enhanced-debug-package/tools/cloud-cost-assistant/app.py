#!/usr/bin/env python3
"""
Cloud Cost Assistant - Web Interface
A conversational AI for cloud cost optimization
"""

from flask import Flask, render_template, request, jsonify
import openai
import subprocess
import json
from datetime import datetime

app = Flask(__name__)

# Configure OpenAI
openai.api_key = "your-openai-api-key"


class CloudCostAssistant:
    def __init__(self):
        self.system_prompt = """
You are an expert cloud cost optimization assistant. You can help users:
1. Analyze Azure and GCP resources
2. Identify cost savings opportunities  
3. Execute optimization commands
4. Provide cost estimates and recommendations

When users ask about costs, you can execute CLI commands and provide analysis.
Be conversational, helpful, and focus on practical cost savings.
"""

    def execute_azure_command(self, command):
        """Execute Azure CLI command safely"""
        try:
            result = subprocess.run(
                f"az {command}", shell=True, capture_output=True, text=True, timeout=30
            )
            return {"success": True, "output": result.stdout, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_gcp_command(self, command):
        """Execute GCP CLI command safely"""
        try:
            result = subprocess.run(
                f"gcloud {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {"success": True, "output": result.stdout, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def chat(self, user_message, conversation_history=[]):
        """Process user message and return AI response"""

        # Add system context and tools
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                functions=[
                    {
                        "name": "execute_azure_command",
                        "description": "Execute Azure CLI command",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "Azure CLI command to execute",
                                }
                            },
                            "required": ["command"],
                        },
                    },
                    {
                        "name": "execute_gcp_command",
                        "description": "Execute Google Cloud CLI command",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "GCP CLI command to execute",
                                }
                            },
                            "required": ["command"],
                        },
                    },
                ],
                function_call="auto",
            )

            message = response.choices[0].message

            # Check if AI wants to call a function
            if message.get("function_call"):
                function_name = message["function_call"]["name"]
                function_args = json.loads(message["function_call"]["arguments"])

                if function_name == "execute_azure_command":
                    result = self.execute_azure_command(function_args["command"])
                elif function_name == "execute_gcp_command":
                    result = self.execute_gcp_command(function_args["command"])

                # Send function result back to AI
                messages.append(message)
                messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(result),
                    }
                )

                # Get final response
                final_response = openai.ChatCompletion.create(
                    model="gpt-4", messages=messages
                )

                return final_response.choices[0].message["content"]

            return message["content"]

        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"


# Initialize assistant
assistant = CloudCostAssistant()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    history = data.get("history", [])

    response = assistant.chat(user_message, history)

    return jsonify({"response": response, "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
