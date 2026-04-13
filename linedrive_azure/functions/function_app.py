import azure.functions as func
import json
import logging
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path to import the scraper
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the AI Agent client
try:
    from agent_client import LinedriveAgentClient

    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    logging.warning("AI Agent client not available")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create the Azure Functions app - V2 Programming Model
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)



@app.route(route="echo", methods=["GET", "POST", "OPTIONS"])
def echo_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Echo function that returns whatever data is sent to it.
    Useful for testing POST requests and JSON payloads.
    """
    logging.info("Echo function called.")

    # Handle OPTIONS request for CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    # Get request method and body
    method = req.method
    url = req.url
    headers = dict(req.headers)

    # Get request body
    body_data = None
    try:
        if req.get_body():
            body_data = req.get_json()
    except (ValueError, UnicodeDecodeError):
        try:
            body_data = req.get_body().decode("utf-8")
        except Exception:
            body_data = "Unable to decode body"

    # Create echo response
    echo_data = {
        "echo": "success",
        "method": method,
        "url": url,
        "headers": {k: v for k, v in headers.items() if not k.startswith("x-")},
        "body": body_data,
        "timestamp": datetime.now().isoformat(),
        "message": "Echo successful - your data was received and returned",
    }

    return func.HttpResponse(
        json.dumps(echo_data, indent=2),
        status_code=200,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )


@app.route(route="ai_agent", methods=["POST", "OPTIONS"])
def ai_agent_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    AI Agent function that processes tournament queries using Azure AI Agents.
    Expects JSON payload with 'message' field.
    """
    logging.info("AI Agent function called.")

    # Handle OPTIONS request for CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    # Check if AI Agent is available
    if not AGENT_AVAILABLE:
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "AI Agent client not available",
                    "message": "The AI Agent functionality is currently unavailable.",
                }
            ),
            status_code=503,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )

    try:
        # Get request body
        req_body = req.get_json()
        if not req_body or "message" not in req_body:
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": "Invalid request",
                        "message": "Request body must contain 'message' field",
                    }
                ),
                status_code=400,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )

        user_message = req_body["message"]
        thread_id = req_body.get(
            "thread_id"
        )  # Optional thread ID for conversation continuity

        # Initialize AI Agent client
        agent_client = LinedriveAgentClient()

        # Create or use existing thread
        if thread_id:
            # Use existing thread
            response = agent_client.send_message(
                thread_id, user_message, show_sources=True
            )
        else:
            # Create new thread
            thread = agent_client.create_thread()
            if thread:
                thread_id = thread.id
                response = agent_client.send_message(
                    thread_id, user_message, show_sources=True
                )
            else:
                raise Exception("Failed to create conversation thread")

        # Check if this is a rate limit retry response
        if not response.get("success") and response.get("error") == "rate_limit_retry":
            return func.HttpResponse(
                json.dumps(
                    {
                        "success": False,
                        "error": "rate_limit_retry",
                        "response": response.get(
                            "response",
                            "System is still thinking, just a few more seconds...",
                        ),
                        "sources": response.get("sources", []),
                        "thread_id": thread_id,
                        "retry_info": response.get("retry_info", {}),
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                status_code=202,  # Accepted - processing
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
            )

        # Check if this is a rate limit exceeded error
        if not response.get("success") and "rate_limit" in response.get("error", ""):
            return func.HttpResponse(
                json.dumps(
                    {
                        "success": False,
                        "error": "rate_limit_exceeded",
                        "response": response.get(
                            "response",
                            "The system is experiencing high demand. Please try again in a few minutes.",
                        ),
                        "sources": response.get("sources", []),
                        "thread_id": thread_id,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                status_code=429,  # Too Many Requests
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Retry-After": "60",  # Suggest retry after 60 seconds
                },
            )

        # Check for other errors
        if not response.get("success"):
            return func.HttpResponse(
                json.dumps(
                    {
                        "success": False,
                        "error": response.get("error", "Unknown error"),
                        "response": response.get("response")
                        or "An error occurred while processing your request.",
                        "sources": response.get("sources", []),
                        "thread_id": thread_id,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                status_code=500,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )

        # Return successful response
        return func.HttpResponse(
            json.dumps(
                {
                    "success": True,
                    "response": response.get("response", ""),
                    "sources": response.get("sources", []),
                    "thread_id": thread_id,  # Use the actual thread_id variable, not from response
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            status_code=200,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    except Exception as e:
        logging.error("Error in AI Agent function: %s", str(e))
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "Internal server error",
                    "message": f"An error occurred while processing your request: {str(e)}",
                }
            ),
            status_code=500,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
