# ==============================================================================
# 1. Import Necessary Libraries
# ==============================================================================
import os
import uuid
import logging
from typing import List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client

# ==============================================================================
# 2. FastAPI Application Setup
# ==============================================================================

# Initialize the main FastAPI application
app = FastAPI(
    title="LLM + MCP Multi-Agent Collaborative API",
    description="An API server that acts as a bridge between a web UI and the MCP agent server."
)

# --- Configure Cross-Origin Resource Sharing (CORS) ---
# This is crucial for allowing the HTML/JavaScript frontend, which is served
# as a local file, to make requests to this backend server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, can be restricted for production.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.).
    allow_headers=["*"],  # Allows all request headers.
)

# --- Configure Logging ---
# Sets up a simple logging format to monitor server activity in the console.
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

# --- Mount Static Files Directory ---
# This makes the 'reports' folder accessible to the browser.
# For example, a file named 'report.docx' can be accessed at:
# http://localhost:5000/reports/report.docx
# We also ensure the directory exists on startup to prevent errors.
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)
app.mount(f"/{REPORTS_DIR}", StaticFiles(directory=REPORTS_DIR), name="reports")


# ==============================================================================
# 3. Helper Function to Connect to the MCP Server
# ==============================================================================

def call_mcp_tool(tool_name: str, arguments: dict):
    """
    Connects to the running MCP server and calls a specified tool with arguments.
    """
    mcp_server_url = "http://localhost:8000/mcp/"
    try:
        logging.info(f"Connecting to MCP server to call tool: '{tool_name}'")
        
        # Initialize the MCP client with the server's transport URL
        client = MCPClient(lambda: streamablehttp_client(mcp_server_url))

        # The 'with' statement ensures the client connection is properly managed
        with client:
            tool_use_id = str(uuid.uuid4())
            # Synchronously call the tool and wait for the result
            result = client.call_tool_sync(tool_use_id, tool_name, arguments)
        
        logging.info(f"Successfully received response from tool: '{tool_name}'")
        return result

    except Exception as e:
        logging.error(f"Failed to call MCP tool '{tool_name}': {e}")
        # Re-raise the exception to be handled by the API endpoint's error block
        raise


# ==============================================================================
# 4. API Endpoints
# ==============================================================================

@app.get("/")
def root():
    """Root endpoint to confirm the server is running."""
    return {"message": "Welcome to the LLM + MCP Collaborative API Server"}

@app.get("/health")
def health_check():
    """Health check endpoint to verify connection to the MCP agent server."""
    try:
        # A lightweight way to check the connection is to list available tools.
        client = MCPClient(lambda: streamablehttp_client("http://localhost:8000/mcp/"))
        with client:
            tools = client.list_tools_sync()
        return {
            "status": "ok",
            "message": "API server is running and connected to MCP server.",
            "tools_available": [t.tool_name for t in tools],
        }
    except Exception as e:
        return {"status": "error", "message": f"Could not connect to MCP server: {e}"}

@app.post("/generate")
async def generate_report(request: Request):
    """
    Main endpoint to generate a collaborative R&D report.
    It receives a project 'idea' and triggers the 'pi_agent' on the MCP server.
    """
    try:
        data = await request.json()
        idea = data.get("idea", "").strip()

        if not idea:
            return {"status": "error", "message": "Field 'idea' is required in the request body."}

        logging.info(f"Received generation request for idea: '{idea}'")
        
        # --- CRITICAL ---
        # Call the 'pi_agent', which is the coordinator agent defined in main_agent_poc_local.py
        result = call_mcp_tool("pi_agent", {"idea": idea})
        
        # The 'pi_agent' returns a JSON object. We extract the file path from it.
        # The result from call_tool_sync is a dictionary, not an object, so use key access.
        if "json" in result and "file_path" in result["json"]:
             filepath = result["json"].get("file_path", "Unknown")
             message = result["json"].get("message", "Report generated.")
        else:
            # Fallback if the response format is unexpected
            filepath = "Unknown"
            message = "Report generation finished, but path could not be extracted."

        logging.info(f"Report generation complete. File saved at: {filepath}")

        return {
            "status": "success",
            "message": message,
            "file_path": filepath,
            "idea": idea,
        }

    except Exception as e:
        logging.error(f"An error occurred during report generation: {e}")
        return {
            "status": "error",
            "message": f"An internal server error occurred: {e}",
        }

@app.get("/list-reports", response_model=List[str])
def list_reports():
    """
    New endpoint to list all .docx files in the reports directory.
    The list is sorted by modification time, with the newest files first.
    """
    try:
        files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".docx") and os.path.isfile(os.path.join(REPORTS_DIR, f))]
        
        # Sort files by last modified time in descending order (newest first)
        files.sort(
            key=lambda f: os.path.getmtime(os.path.join(REPORTS_DIR, f)),
            reverse=True
        )
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
    print("🚀 Starting FastAPI server for LLM + MCP Collaborative System...")
    print(f"📂 Serving reports from: ./{REPORTS_DIR}")
    print("🔗 Access the API at: http://localhost:5000")
    
    # Run the server using uvicorn. 'reload=True' is great for development.
    uvicorn.run("api_server:app", host="0.0.0.0", port=5000, reload=True)