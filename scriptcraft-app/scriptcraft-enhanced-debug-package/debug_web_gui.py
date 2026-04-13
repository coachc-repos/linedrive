#!/usr/bin/env python3
"""
ScriptCraft Web GUI - Enhanced with Debug Info
"""

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    make_response,
    render_template_string,
)
from flask_cors import CORS
import threading
import webbrowser
import time
import sys
import logging
import datetime
import tempfile
import asyncio
import os
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add current directory to Python path for local imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


class ScriptCraftWeb:
    def __init__(self):
        self.current_script = ""
        self.last_result = ""
        self.agent_available = False
        self.agent_error = None
        logger.info("Initializing ScriptCraftWeb...")

        # Check environment
        api_key = os.environ.get("AI_PROJECT_API_KEY")
        logger.info(f"API Key present: {bool(api_key)}")
        if api_key:
            logger.info(f"API Key: {api_key[:10]}...{api_key[-4:]}")

        # Try to initialize the actual AI agent with timeout
        try:
            logger.info("Attempting to initialize Azure AI agent...")

            # Import with timeout
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Agent initialization timed out")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)  # 30 second timeout

            try:
                from linedrive_azure.agents.script_polisher_agent_client import (
                    ScriptPolisherAgentClient,
                )

                self.agent = ScriptPolisherAgentClient()
                self.agent_available = True
                logger.info("✅ Azure AI agent initialized successfully!")
            finally:
                signal.alarm(0)  # Cancel the alarm

        except TimeoutError:
            logger.error("❌ Azure AI agent initialization timed out after 30 seconds")
            self.agent_available = False
            self.agent_error = "Initialization timeout"
        except Exception as e:
            logger.error(f"❌ Could not initialize AI agent: {e}")
            self.agent_available = False
            self.agent_error = str(e)

    def create_script_mock(self, user_prompt: str) -> dict:
        """Create a mock script when Azure agent is not available"""
        logger.info("Using mock script creation")

        mock_script = f"""# Mock Script Generated
# Based on prompt: {user_prompt}

FADE IN:

EXT. LOCATION - DAY

[This is a mock script created because the Azure AI agent is not available]

CHARACTER
    {user_prompt[:100]}...

FADE OUT.

THE END
"""

        return {
            "success": True,
            "script": mock_script,
            "agent_used": "mock-agent",
            "note": "This is a mock script. Azure AI agent was not available.",
        }

    def create_script_with_agent(self, user_prompt: str) -> dict:
        """Create script using the actual Azure AI agent"""
        try:
            logger.info(f"Creating script with agent for prompt: {user_prompt[:50]}...")

            # Create thread
            thread = self.agent.create_thread()
            logger.info(f"Thread created: {thread.id}")

            # Send message with timeout
            result = self.agent.send_message(
                thread_id=thread.id,
                message_content=f"Create a script based on this prompt: {user_prompt}",
                timeout=60,  # 60 second timeout
            )

            if result["success"]:
                logger.info("✅ Script created successfully with Azure AI agent")
                return {
                    "success": True,
                    "script": result["response"],
                    "agent_used": "azure-ai-agent",
                    "sources": result.get("sources", []),
                }
            else:
                logger.error(f"❌ Azure AI agent failed: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"],
                    "fallback_used": True,
                }

        except Exception as e:
            logger.error(f"❌ Exception in script creation: {e}")
            return {"success": False, "error": str(e), "fallback_used": True}


# Initialize the ScriptCraft instance
scriptcraft = ScriptCraftWeb()


@app.route("/")
def index():
    """Main page with debug info"""
    return render_template_string(
        """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ScriptCraft AI - Debug Mode</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; margin-bottom: 30px; }
        .debug-info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #3498db; }
        .status { font-weight: bold; margin-bottom: 10px; }
        .status.success { color: #27ae60; }
        .status.error { color: #e74c3c; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
        input, textarea { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px; box-sizing: border-box; }
        textarea { height: 120px; resize: vertical; }
        button { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-right: 10px; }
        button:hover { background: #2980b9; }
        button:disabled { background: #bdc3c7; cursor: not-allowed; }
        #output { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px; border: 1px solid #e9ecef; min-height: 100px; }
        .loading { color: #3498db; }
        .error { color: #e74c3c; }
        .success { color: #27ae60; }
        pre { white-space: pre-wrap; background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 ScriptCraft AI - Debug Mode</h1>
        
        <div class="debug-info">
            <h3>🔧 System Status</h3>
            <div class="status {{ 'success' if agent_available else 'error' }}">
                Azure AI Agent: {{ 'Available ✅' if agent_available else 'Not Available ❌' }}
            </div>
            {% if not agent_available and agent_error %}
            <div style="color: #e74c3c; font-size: 12px; margin-top: 5px;">
                Error: {{ agent_error }}
            </div>
            {% endif %}
            <div style="margin-top: 10px; font-size: 12px; color: #7f8c8d;">
                API Key: {{ 'Present ✅' if api_key_present else 'Missing ❌' }}<br>
                Python Path: {{ python_path }}<br>
                Flask Mode: Debug
            </div>
        </div>

        <div class="form-group">
            <label for="prompt">Script Prompt:</label>
            <textarea id="prompt" placeholder="Describe the script you want to create...">A 30-second commercial about coffee that energizes people</textarea>
        </div>

        <button onclick="createScript()" id="createBtn">Create Script</button>
        <button onclick="testConnection()" id="testBtn">Test Azure Connection</button>

        <div id="output"></div>
    </div>

    <script>
        function createScript() {
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) {
                alert('Please enter a script prompt');
                return;
            }

            const createBtn = document.getElementById('createBtn');
            const output = document.getElementById('output');
            
            createBtn.disabled = true;
            createBtn.textContent = 'Creating...';
            output.innerHTML = '<div class="loading">🎬 Creating your script...</div>';

            fetch('/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt })
            })
            .then(response => response.json())
            .then(data => {
                createBtn.disabled = false;
                createBtn.textContent = 'Create Script';
                
                if (data.success) {
                    output.innerHTML = `
                        <div class="success">✅ Script created successfully!</div>
                        <div style="margin: 10px 0; font-size: 12px; color: #7f8c8d;">
                            Agent: ${data.agent_used || 'unknown'}
                            ${data.note ? ' | ' + data.note : ''}
                        </div>
                        <pre>${data.script}</pre>
                    `;
                } else {
                    output.innerHTML = `
                        <div class="error">❌ Failed to create script</div>
                        <div style="margin: 10px 0; color: #e74c3c;">
                            Error: ${data.error || 'Unknown error'}
                        </div>
                    `;
                }
            })
            .catch(error => {
                createBtn.disabled = false;
                createBtn.textContent = 'Create Script';
                output.innerHTML = `<div class="error">❌ Network error: ${error.message}</div>`;
            });
        }

        function testConnection() {
            const testBtn = document.getElementById('testBtn');
            const output = document.getElementById('output');
            
            testBtn.disabled = true;
            testBtn.textContent = 'Testing...';
            output.innerHTML = '<div class="loading">🔍 Testing Azure connection...</div>';

            fetch('/test-azure')
            .then(response => response.json())
            .then(data => {
                testBtn.disabled = false;
                testBtn.textContent = 'Test Azure Connection';
                
                output.innerHTML = `
                    <div class="${data.success ? 'success' : 'error'}">
                        ${data.success ? '✅' : '❌'} Azure Connection Test
                    </div>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            })
            .catch(error => {
                testBtn.disabled = false;
                testBtn.textContent = 'Test Azure Connection';
                output.innerHTML = `<div class="error">❌ Test failed: ${error.message}</div>`;
            });
        }
    </script>
</body>
</html>
    """,
        agent_available=scriptcraft.agent_available,
        agent_error=scriptcraft.agent_error,
        api_key_present=bool(os.environ.get("AI_PROJECT_API_KEY")),
        python_path=os.environ.get("PYTHONPATH", "not set"),
    )


@app.route("/create", methods=["POST"])
def create_script():
    """Create script endpoint with fallback"""
    try:
        data = request.json
        prompt = data.get("prompt", "").strip()

        if not prompt:
            return jsonify({"success": False, "error": "No prompt provided"})

        if scriptcraft.agent_available:
            # Try Azure AI agent
            result = scriptcraft.create_script_with_agent(prompt)
            if result["success"]:
                return jsonify(result)
            else:
                # Fall back to mock
                logger.info("Azure agent failed, falling back to mock")
                mock_result = scriptcraft.create_script_mock(prompt)
                mock_result["azure_error"] = result.get("error")
                return jsonify(mock_result)
        else:
            # Use mock directly
            return jsonify(scriptcraft.create_script_mock(prompt))

    except Exception as e:
        logger.error(f"Error in create_script: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/test-azure")
def test_azure():
    """Test Azure connection endpoint"""
    try:
        api_key = os.environ.get("AI_PROJECT_API_KEY")

        result = {
            "success": False,
            "api_key_present": bool(api_key),
            "api_key_partial": f"{api_key[:10]}...{api_key[-4:]}" if api_key else None,
            "agent_available": scriptcraft.agent_available,
            "agent_error": scriptcraft.agent_error,
            "python_path": os.environ.get("PYTHONPATH"),
            "tests": {},
        }

        # Test 1: Basic imports
        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential

            result["tests"]["imports"] = "✅ Success"
        except Exception as e:
            result["tests"]["imports"] = f"❌ Failed: {e}"
            return jsonify(result)

        # Test 2: Credential creation
        try:
            credential = DefaultAzureCredential()
            result["tests"]["credential"] = "✅ Success"
        except Exception as e:
            result["tests"]["credential"] = f"❌ Failed: {e}"
            return jsonify(result)

        # Test 3: Project client
        if api_key:
            try:
                project = AIProjectClient(
                    credential=credential,
                    api_key=api_key,
                    endpoint="https://linedrive-ai-foundry.services.ai.azure.com/api/projects/linedriveAgents",
                )
                result["tests"]["project_client"] = "✅ Success"
                result["success"] = True
            except Exception as e:
                result["tests"]["project_client"] = f"❌ Failed: {e}"
        else:
            result["tests"]["project_client"] = "❌ No API key"

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    print("🎬 Starting ScriptCraft Debug Server on port 5007...")
    print(
        f"   Agent Status: {'Available' if scriptcraft.agent_available else 'Not Available'}"
    )
    print(
        f"   API Key: {'Present' if os.environ.get('AI_PROJECT_API_KEY') else 'Missing'}"
    )
    app.run(host="0.0.0.0", port=5007, debug=True)
