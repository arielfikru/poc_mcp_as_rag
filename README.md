# Multi-Agent AI Orchestrator

This project is a Proof of Concept (PoC) for a **Multi-Agent** architecture based on the **Model Context Protocol (MCP)**. It simulates a corporate system environment undergoing compliance and security auditing, where a Large Language Model (LLM) acts as an intelligent *ReAct Agent*. The orchestrator coordinates with multiple "MCP Servers" (AI Agents) simultaneously to answer complex questions requiring data from various departments such as HR, Database/Payroll, and IT Security/Compliance.

## Architecture

The architecture consists of one **Orchestrator** (MCP Client) and 3 **MCP Servers** categorized by domain.

1. **Orchestrator (`orchestrator.py`)**
   - Acts as the main MCP Client.
   - Connects to the OpenRouter API (using `z-ai/glm-5.1` by default) for its cognitive capabilities.
   - Executes a *ReAct (Reasoning and Acting) loop* (up to 5 iterations) to break down and solve complex instructions.
   - Aggregates the results of *Tool Calls* from the MCP servers to provide a final, comprehensive answer.

2. **Agent A - Database & Payroll (`server_a_postgres.py`)**
   - Provides access to the employee database (SQLite-based).
   - Manages records including ID, name, department, role, salary, and email.
   - Available tools:
     - `get_user_info(user_id)`
     - `search_employee_by_name(name)`
     - `list_employees()`
     - `get_department_summary()`
     - `check_salary_anomaly(salary, role)`

3. **Agent B - HR Knowledge Base (`server_b_hr.py`)**
   - Handles the retrieval of Human Resources knowledge and guidelines.
   - Reads *Markdown* documents from the `knowledge_base/hr` directory.
   - Available tools:
     - `search_hr_docs(query)`

4. **Agent C - IT Policy & Audit Server (`server_c_it.py`)**
   - Responsible for IT policy enforcement, access control matrices, and audit compliance documents.
   - Utilizes an Access Matrix based on employee `role` profiles.
   - Reads *Markdown* documents from `knowledge_base/it` and `knowledge_base/auditor` directories.
   - Available tools:
     - `search_it_policies(query, role)`
     - `search_audit_policies(query)`
     - `search_monitoring_docs(query)`
     - `check_access_violation(role, system)`

## Prerequisites

- Python 3.10+ recommended
- OpenRouter API Key (`OPENROUTER_API_KEY`) placed inside a `.env` file!
- Standard Python MCP modules (e.g., `mcp`, `mcp.server.fastmcp`)

## How to Let it Run

1. **Environment Configuration**
   Create a `.env` file in the root directory and add your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-xxx...
   ```

2. **Install Dependencies**
   It is recommended to use a virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate
   # On Windows: venv\Scripts\activate
   pip install mcp openai python-dotenv
   ```
   *(Please adjust versions based on your specific ecosystem needs)*

3. **Running the Orchestrator**
   You can execute the orchestrator with any free-text questions via command line arguments.
   If no arguments are provided, a default complex prompt will be executed.

   ```bash
   python orchestrator.py "Please check employee ID 104, verify if there are any salary anomalies, and check if they are authorized to access the finance_system."
   ```

## Workflow & ReAct Loop

When the orchestrator is executed:
1. The program spins up and loads the 3 MCP Servers separately utilizing standard I/O streams (StdioTransport).
2. The system scans and catalogs all available *tools* from these servers.
3. The user prompt is sent to the LLM alongside the definitions of these tools.
4. The LLM decides which tools to invoke based on its reasoning process ("*Tool Call*").
5. The MCP Client (orchestrator) routes the *Tool Call* to the specific Agent responsible for the function.
6. This processing loop continues until the LLM determines it has entirely answered the prompt without needing further tools, or until it hits the hard limit of 5 iterations.
