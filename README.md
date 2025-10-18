# Project Jigsaw
### When Multi-Agents and LLMs Collaborate to Write Project Proposals

![Project Jigsaw Dashboard](UI.jpg) 

This project is a dashboard that demonstrates how a **Collaborative Learning "Jigsaw" architecture** can coordinate multiple specialized LLM agents to autonomously generate comprehensive project proposals.

The system simulates a real-world project lifecycle, where different "AI Specialists" (powered by Google's Gemini LLM via MCP) work in phases to build a complete report.

## 🚀 Core Features

* **Jigsaw Architecture**: Based on collaborative learning theory, tasks are divided among specialized agents (e.g., Background, Market, Technical) and then synthesized by a "PI Agent" (Coordinator).
* **Dynamic Lifecycle UI**: A visual dashboard (built with HTML/JS) that simulates the project's phases in real-time, from Feasibility to Planning to final Synthesis.
* **Multi-Agent Backend**: Uses the **MCP (Multi-Agent Collaboration Protocol)** framework (`main_agent_poc_local.py`) to manage and expose different AI expert tools.
* **API-Driven**: A **FastAPI** backend (`api_server.py`) serves as a bridge between the web UI and the MCP agent server.
* **Automatic Report Generation**: Generates a complete project proposal in a `.docx` Word document format.

## 🛠️ System Architecture

The project runs on three main components that work in concert:

1.  **`index.html` (Frontend)**: The "Project Lifecycle Dashboard" UI. You type in an idea, and it visualizes the entire collaboration process phase by phase.
2.  **`api_server.py` (Backend Bridge)**: A FastAPI server that receives the project idea from the UI, lists reports, and makes the appropriate call to the MCP server.
3.  **`main_agent_poc_local.py` (Agent Server)**: The MCP server where each "AI Specialist" is defined as a tool. This is the "brain" of the operation, where the LLM calls happen.

## ⚙️ How to Run

Follow these steps to get the project running locally.

### 1. Clone the Repository

```bash
git clone [https://github.com/hxyair/Project-Jigsaw]
cd Project-Jigsaw
```

### 2. Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate

# Install all required dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials

This project requires Google Cloud credentials (for the Vertex AI/Gemini API).

1.  **Environment Variables**: Copy the template file and fill in your details.
    ```bash
    cp .env.example .env
    ```
    ...then open `.env` and add your `GOOGLE_PROJECT_ID` etc.

2.  **Service Account**:
    * Go to your Google Cloud Console and create a service account.
    * Download the JSON key file.
    * Rename it to `credentials.json` and place it in the project's root directory. (The `.gitignore` file will prevent it from being uploaded).

### 4. Run the Application

You need to run **two** servers in **two separate terminals**.

**Terminal 1: Run the MCP Agent Server**
```bash
python main_agent_poc_local.py
```

**Terminal 2: Run the FastAPI Server**
```bash
uvicorn api_server:app --reload --port 5000
```

### 5. Open the Dashboard

* Open the `index.html` file directly in your browser (e.g., Chrome, Firefox).
* Enter a project idea and click "Initiate Project Lifecycle"!

Generated reports will appear in the `reports/` directory.