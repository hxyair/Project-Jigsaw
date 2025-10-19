# ==============================================================================
# api_server.py
#
# Final Corrected Version (Client-Side) - Fixes SyntaxError.
# - Relies on the faster, concurrent server-side execution.
# - Uses default timeouts for MCP client connection.
# - Includes standard error handling.
# - All comments are in English.
# ==============================================================================
import os
import uuid
import logging
from typing import List
import json # Ensure json is imported

import uvicorn
import httpx # Import httpx (used implicitly and for TimeoutError)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from strands.tools.mcp.mcp_client import MCPClient # Correct import path
from mcp.client.streamable_http import streamablehttp_client
# Import specific exceptions if needed for more granular error handling
from strands.types.exceptions import MCPClientInitializationError
from mcp.shared.exceptions import McpError

# ==============================================================================
# 2. FastAPI Application Setup
# ==============================================================================
app = FastAPI(
    title="LLM + MCP Multi-Agent Collaborative API",
    description="API server bridging UI and MCP agent server."
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

# Mount Static Files Directory ('reports')
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)
app.mount(f"/{REPORTS_DIR}", StaticFiles(directory=REPORTS_DIR), name="reports")
logging.info(f"📂 Serving reports from directory: '{REPORTS_DIR}'")

# ==============================================================================
# 3. Helper Function to Connect to the MCP Server (Standard Timeout)
# ==============================================================================
MCP_SERVER_URL = "http://localhost:8000/mcp/"

def create_standard_transport():
    """Creates a standard MCP transport client with default timeouts."""
    # Use default timeouts provided by the library / httpx
    return streamablehttp_client(MCP_SERVER_URL)

def call_mcp_tool(tool_name: str, arguments: dict):
    """
    Connects to the MCP server and calls a specified tool with arguments,
    using default timeouts. Handles potential errors including timeouts.
    """
    client = None
    try:
        logging.info(f"Connecting to MCP server ({MCP_SERVER_URL}) to call tool: '{tool_name}'...")
        # Use the standard factory function
        client = MCPClient(create_standard_transport)

        with client:
            tool_use_id = str(uuid.uuid4())
            logging.info(f"Calling tool '{tool_name}' with ID: {tool_use_id}. Waiting for completion (default timeout)...")
            # Synchronously call the tool and wait
            result = client.call_tool_sync(tool_use_id, tool_name, arguments)

        if result is None:
             logging.error(f"❌ MCP call for {tool_name} returned None.")
             raise Exception(f"MCP tool call '{tool_name}' returned no result.")

        logging.info(f"Successfully received response from tool: '{tool_name}'")
        return result

    # Catch potential timeout errors (even with default timeout)
    except (httpx.ReadTimeout, TimeoutError) as timeout_err:
        logging.error(f"❌ MCP call timed out waiting for '{tool_name}': {timeout_err}")
        # Re-raise as a standard TimeoutError for the endpoint handler
        raise TimeoutError(f"Operation timed out waiting for agent '{tool_name}'. Check server logs.") from timeout_err
    except MCPClientInitializationError as init_err:
        logging.error(f"❌ MCP client failed to initialize when calling '{tool_name}': {init_err}")
        raise MCPClientInitializationError(f"Failed to connect to MCP server for tool '{tool_name}'. Check if server is running.") from init_err
    except McpError as mcp_err:
         logging.error(f"❌ MCP Error during call to '{tool_name}': {mcp_err}")
         # Check specific McpError types if needed
         if "Connection closed" in str(mcp_err): # Example check
              raise TimeoutError(f"MCP connection closed unexpectedly during call to '{tool_name}', possibly due to server issue or timeout.") from mcp_err
         else:
              raise mcp_err # Re-raise other MCP errors
    except Exception as e:
        logging.error(f"❌ Unexpected error during MCP call for '{tool_name}': {type(e).__name__} - {e}")
        raise e

# ==============================================================================
# 4. API Endpoints
# ==============================================================================
@app.get("/")
def root():
    return {"message": "Welcome to the LLM + MCP Collaborative API Server"}

@app.get("/health")
def health_check():
    """Health check endpoint using standard timeouts."""
    client = None
    try:
        client = MCPClient(create_standard_transport)
        with client:
            tools = client.list_tools_sync() # This is usually a quick operation
        logging.info("Health check successful: Connected to MCP server.")
        return {
            "status": "ok",
            "message": "API server running & connected to MCP server.",
            "tools_available": [t.tool_name for t in tools],
        }
    except Exception as e:
        logging.error(f"❌ Health check failed: MCP connection error: {type(e).__name__} - {e}")
        return {"status": "error", "message": f"MCP connection failed: {e}. Check if MCP server (main_agent_poc_local.py) is running."}

@app.post("/generate")
async def generate_report(request: Request):
    """
    Main endpoint to generate a collaborative R&D report.
    Relies on the now-faster server-side execution.
    """
    try:
        data = await request.json()
        idea = data.get("idea", "").strip()

        if not idea:
            logging.warning("Received generate request with empty 'idea'.")
            return {"status": "error", "message": "Field 'idea' is required."}

        logging.info(f"Received generation request for idea: '{idea[:50]}...'")

        # Call the PI agent using the helper function (now with default timeout)
        result = call_mcp_tool("pi_agent", {"idea": idea})

        # Process the result from pi_agent
        filepath = "Unknown"
        message = "Report generation process finished, but outcome details unclear."
        final_status = "error" # Default to error

        # --- Refined Result Processing ---
        if isinstance(result, dict):
            # Primary check: 'json' field with structured data from pi_agent
            if "json" in result and isinstance(result["json"], dict):
                pi_agent_response = result["json"]
                filepath = pi_agent_response.get("file_path", "Unknown")
                message = pi_agent_response.get("message", "Synthesis complete.")
                # Trust the status reported by the PI agent if available
                pi_status = pi_agent_response.get("status")
                if pi_status == "success" or pi_status == "partial_success":
                    final_status = "success" # Treat partial success as overall success for UI
                    log_level = logging.INFO if pi_status == "success" else logging.WARNING
                    logging.log(log_level, f"Report generation status '{pi_status}'. Path: {filepath}")
                    if "✅" not in message and "⚠️" not in message: message = ("✅ " if pi_status == "success" else "⚠️ ") + message
                else:
                    final_status = "error"; message = pi_agent_response.get("message", "PI Agent reported an unspecified error."); logging.error(f"PI agent reported error status: {message}")

            # Fallback: Check 'content' field for text (less reliable)
            elif "content" in result and result["content"] and isinstance(result["content"], list):
                 content_block = result["content"][0]
                 if "text" in content_block and isinstance(content_block["text"], str):
                      output_text = content_block["text"].strip()
                      # Simple check based on keywords in the text response
                      if "saved" in output_text.lower() and "✅" in output_text:
                           final_status = "success"
                           message = output_text
                           try:
                               # Attempt to extract filepath robustly
                               path_part = output_text.split("saved:")[-1].strip()
                               # --- CORRECTED INDENTATION AREA ---
                               if os.path.exists(path_part): # Basic check if path looks valid
                                    filepath = path_part
                           except Exception:
                               logging.warning("Could not parse filepath reliably from text.")
                           # Correctly indented log statement
                           logging.info(f"Report likely generated (parsed from text). Path: {filepath}")
                           # --- END CORRECTION ---
                      elif "error" in output_text.lower() or "failed" in output_text.lower():
                           final_status = "error"
                           message = output_text
                           logging.error(f"PI agent returned text indicating error: {output_text}")
                      else:
                          # Ambiguous text response
                          final_status = "error" # Assume error if unclear
                          message = "Received unclear text response from PI agent: " + output_text
                          logging.warning(message)
                 else:
                     logging.warning(f"Received unexpected content block structure from PI agent: {content_block}")
            else:
                 logging.warning(f"Received unexpected result structure from PI agent (no json or valid content): {result}")
        else:
             logging.error(f"Received unexpected result type from PI agent call: {type(result)}")

        # --- Return response ---
        return {
            "status": final_status,
            "message": message,
            "file_path": filepath,
            "idea": idea,
        }

    except TimeoutError as te: # Catch the specific timeout from call_mcp_tool
        logging.error(f"❌ Report generation timed out client-side: {te}")
        return {
            "status": "error",
            "message": f"Operation timed out waiting for the agent server. The server might be overloaded or stuck. Please check server logs or try again later.",
        }
    except MCPClientInitializationError as init_err: # Catch specific connection error
         logging.error(f"❌ Failed to connect to MCP server during generation: {init_err}")
         return {
            "status": "error",
            "message": f"Could not connect to the agent server. Please ensure it's running. Details: {init_err}",
         }
    except Exception as e:
        # Catch all other exceptions during the process
        logging.exception(f"❌ Unhandled error during report generation: {e}") # Log full traceback
        return {
            "status": "error",
            "message": f"An internal server error occurred ({type(e).__name__}). Check server logs for details.",
        }

@app.get("/list-reports", response_model=List[str])
def list_reports():
    """Lists .docx files in the reports directory, newest first."""
    # This function remains unchanged
    try:
        files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".docx") and os.path.isfile(os.path.join(REPORTS_DIR, f))]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(REPORTS_DIR, f)), reverse=True)
        logging.info(f"Found {len(files)} reports in '{REPORTS_DIR}'.")
        return files
    except FileNotFoundError:
        logging.warning(f"Reports directory not found at: '{REPORTS_DIR}'")
        return []
    except Exception as e:
        logging.error(f"Failed to list reports: {e}")
        return []

# ==============================================================================
# 5. Server Entry Point
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Starting FastAPI server for LLM + MCP Collaboration...")
    print(f"📂 Serving reports from: ./{REPORTS_DIR}")
    print(f"🔗 API server running on http://localhost:5000")
    print(f"🔌 Expecting MCP server at {MCP_SERVER_URL}")
    print(f"⏱️ Using default MCP client timeouts.") # Updated log message

    uvicorn.run("api_server:app", host="0.0.0.0", port=5000, reload=True)