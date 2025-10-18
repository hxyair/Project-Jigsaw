import os
from datetime import datetime
from docx import Document
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import vertexai
from vertexai.generative_models import GenerativeModel

# ==============================================================================
# 1. Load environment variables
# ==============================================================================
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "your-project-id")
LOCATION = os.getenv("GOOGLE_LOCATION", "asia-southeast1")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", "credentials.json"
)

# ==============================================================================
# 2. Initialize Vertex AI model
# ==============================================================================
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel("gemini-2.5-flash")
    print(f"✅ Vertex AI initialized: project={PROJECT_ID}, region={LOCATION}")
except Exception as e:
    print("⚠️ Vertex AI initialization failed. Please check .env or credentials.")
    print(e)
    exit(1)

# ==============================================================================
# 3. Helper: Save report as Word document
# ==============================================================================
def save_to_word(idea: str, content: str) -> str:
    """Save generated collaborative report as a Word file."""
    short_title = "_".join(idea.split()[:4])
    date_suffix = datetime.now().strftime("%m%d")
    filename = f"{short_title}-{date_suffix}.docx"

    # Ensure the reports folder exists
    os.makedirs("reports", exist_ok=True)
    filepath = os.path.join("reports", filename)

    doc = Document()
    doc.add_heading(f"Collaborative R&D Project Report: {idea}", level=1)
    doc.add_paragraph(content)
    doc.save(filepath)

    print(f"✅ Word report saved: {filepath}")
    return os.path.abspath(filepath)

# ==============================================================================
# 4. Start Collaborative MCP Server
# ==============================================================================
mcp = FastMCP("Collaborative R&D Planning Server")

# --------------------------------------------------------------------------
# Agent: Background Research
# --------------------------------------------------------------------------
@mcp.tool(description="Conduct background research for the project idea.")
def background_agent(idea: str) -> str:
    prompt = f"""
    Conduct detailed background research for this project:
    {idea}

    Include: problem statement, related works, current state of the art,
    and gaps that justify the need for this research.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------------------------------
# Agent: Technical Development
# --------------------------------------------------------------------------
@mcp.tool(description="Describe technical framework and methodology.")
def technical_agent(idea: str) -> str:
    prompt = f"""
    Describe the technical framework for this project:
    {idea}

    Include: proposed architecture, core algorithms, system components,
    and technical innovations.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------------------------------
# Agent: Market Research
# --------------------------------------------------------------------------
@mcp.tool(description="Analyze market context and commercial opportunities.")
def market_agent(idea: str) -> str:
    prompt = f"""
    Conduct market analysis for this project:
    {idea}

    Include: potential applications, target industries, market size,
    competitors, and commercialization potential.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------------------------------
# Agent: Budget and Resource Planning
# --------------------------------------------------------------------------
@mcp.tool(description="Estimate a one-year R&D budget and resource plan.")
def budget_agent(idea: str) -> str:
    prompt = f"""
    Estimate a one-year R&D budget for this project:
    {idea}

    Include: human resources, equipment, software, cloud services,
    and contingency costs in clear bullet points or a simple table.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------------------------------
# Agent: Planning and Timeline
# --------------------------------------------------------------------------
@mcp.tool(description="Propose a work plan and project milestones.")
def planner_agent(idea: str) -> str:
    prompt = f"""
    Propose a timeline and project milestones for this R&D project:
    {idea}

    Include: project phases, expected outputs, and key performance indicators (KPIs).
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------------------------------
# Agent: Impact and Significance
# --------------------------------------------------------------------------
@mcp.tool(description="Assess expected impact and benefits of the project.")
def impact_agent(idea: str) -> str:
    prompt = f"""
    Assess the broader impacts and benefits of this project:
    {idea}

    Include: technological impact, societal relevance, academic contributions,
    and alignment with national or institutional priorities.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------------------------------
# PI Agent (Principal Investigator): Integrate all experts’ work
# --------------------------------------------------------------------------
@mcp.tool(description="Coordinate all experts’ outputs and compile the final R&D report.")
def pi_agent(idea: str):
    """Integrate all expert sections into a single R&D report and return structured JSON."""
    print(f"🧠 [PI Agent] Coordinating collaborative project report for: {idea}")

    background = background_agent(idea)
    technical = technical_agent(idea)
    market = market_agent(idea)
    budget = budget_agent(idea)
    planner = planner_agent(idea)
    impact = impact_agent(idea)

    report = f"""
    === Collaborative R&D Project Report ===

    🧩 Project Title: {idea}

    --- Background Research ---
    {background}

    --- Technical Framework ---
    {technical}

    --- Market Analysis ---
    {market}

    --- Budget & Resources ---
    {budget}

    --- Project Plan ---
    {planner}

    --- Impact & Significance ---
    {impact}

    --- Summary (Prepared by PI Agent) ---
    This report represents the integrated effort of all domain experts under
    the collaborative learning framework. The PI Agent synthesized and refined
    each contribution to form a coherent, actionable R&D proposal.
    """

    filepath = save_to_word(idea, report)

    # Return structured JSON so API server can parse it
    return {
        "status": "success",
        "message": f"✅ Collaborative report saved locally: {filepath}",
        "file_path": filepath,
    }

# ==============================================================================
# 5. Run MCP Server
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Starting Collaborative MCP Server...")
    mcp.run(transport="streamable-http")
