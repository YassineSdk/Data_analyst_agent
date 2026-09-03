# DA Agent

DA Agent is a conversational data analysis assistant built with Chainlit, LangGraph, LangChain, Groq-hosted LLMs, PostgreSQL, pandas, and Plotly. It lets users ask business questions in natural language, converts those questions into safe SQL, executes the SQL against a sales database, explains the results, and optionally returns interactive charts.

The project is designed around a multi-agent workflow where each step has a focused responsibility: intent understanding, SQL generation, SQL auditing, query execution, result interpretation, and visualization planning.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Agent Workflow](#agent-workflow)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Data Model](#data-model)
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Using the Assistant](#using-the-assistant)
- [Configuration](#configuration)
- [Prompt System](#prompt-system)
- [Visualization System](#visualization-system)
- [Development Notes](#development-notes)
- [Troubleshooting](#troubleshooting)
- [Roadmap Ideas](#roadmap-ideas)

## Features

- Natural-language business analytics interface.
- Chainlit chat UI with starter questions for common sales analysis tasks.
- LangGraph orchestration with checkpointed conversation state.
- Intent classification to reject non-analytics requests.
- Clarification loop for ambiguous analytical questions.
- Structured LLM outputs using Pydantic models.
- PostgreSQL SQL generation from validated analytical intent.
- SQL audit step before execution to reduce unsafe or incorrect queries.
- Read-only analytics workflow.
- PostgreSQL query execution through `psycopg`.
- Result analysis written for non-technical users.
- Optional Plotly chart generation.
- User-controlled visualization toggle.
- User-controlled retry setting in the Chainlit settings panel.
- Rich console logging for local development.

## Architecture

The application is organized as a graph of specialized nodes. The user interacts with Chainlit, and Chainlit sends each message into the compiled LangGraph agent.

```text
User
  |
  v
Chainlit UI
  |
  v
LangGraph Agent
  |
  +--> Intent Analyst
  |      |
  |      +--> Out-of-domain response
  |      |
  |      +--> Clarification interrupt
         |
         +--> Clarification interrupt
  |
  +--> SQL Generator
  |
  +--> SQL Auditor
  |      |
  |      +--> Approved: execute SQL
  |      |
  |      +--> Rejected: return to SQL Generator
  |
  +--> SQL Executor
  |
  +--> Result Analyst
  |
  +--> Plot Builder
  |
  v
Final answer and optional Plotly charts
```

### Main Components

| Component | File | Purpose |
| --- | --- | --- |
| Chainlit app | `src/inference.py` | Handles chat startup, user messages, settings, interruptions, final responses, and chart rendering. |
| Graph definition | `src/graph.py` | Defines the LangGraph nodes, edges, routing functions, and compiled agent. |
| Node logic | `src/nodes.py` | Implements each workflow step: intent, SQL, audit, execution, analysis, plots, and fallback response. |
| LLM setup | `src/agents.py` | Initializes the chat model and binds prompts to structured Pydantic outputs. |
| State schema | `src/state.py` | Defines the shared LangGraph state. |
| Data models | `src/models.py` | Defines structured objects for messages, SQL, audits, execution results, intent, and plots. |
| SQL execution | `src/excuter.py` | Connects to PostgreSQL and executes generated SQL. |
| Plot generation | `src/plotfunc.py` | Converts execution results into Plotly figures. |
| Utilities | `src/utils.py` | Loads prompts/context and merges graph state history. |
| Logging | `src/logger.py` | Configures Rich-based application logging. |
| Data context | `data_context.txt` | Describes the available tables, columns, relationships, metrics, and data-quality notes. |
| Prompts | `prompts/*.yaml` | Stores the system prompts for each specialized LLM role. |

## Agent Workflow

### 1. Chat Session Start

When a Chainlit chat starts, `src/inference.py` creates a unique `thread_id` and stores it in the user session. This thread ID is passed into LangGraph so the in-memory checkpointer can keep the conversation state for the session.

The app also exposes two settings:

- `Max_retries`: intended retry limit for workflow behavior.
- `Generate visualizations`: enables or disables Plotly chart generation.

### 2. Intent Analysis

The `intent_analyst` node determines whether the user is asking an analytics question that can be answered with the available data.

It returns an `IntentState` containing:

- `is_analytics_query`
- `interpretation`
- `feedback`
- `needs_clarification`
- `clarification`

If the request is not analytical, the graph routes to the `out_of_domain` node and returns a polite domain-specific response.

If the request is analytical but ambiguous, the graph raises a LangGraph interrupt. Chainlit catches the interrupt and asks the user one clarification question.

### 3. SQL Generation

The `sql_generator` node receives:

- Original user query.
- Database context from `data_context.txt`.
- Validated analytical intent.
- Clarification feedback, when available.

It returns an `SQLState` containing:

- SQL query.
- Explanation.
- Tables used.
- Columns used.

### 4. SQL Audit

The `sql_auditor` node reviews the generated query before execution.

The audit checks:

- Query is read-only.
- No destructive operations are present.
- Tables and columns exist in the provided context.
- Metrics, joins, filters, dates, aggregations, comparisons, and ordering match the intent.
- Join grain does not obviously duplicate rows.

If approved, the graph continues to execution. If rejected, the graph routes back to SQL generation.

### 5. SQL Execution

The `execute` node calls `SQLExecutor.execute()` from `src/excuter.py`.

The executor:

- Opens a PostgreSQL connection using `CONNECTION_STRING`.
- Executes the SQL query.
- Returns column names and result rows.
- Captures and returns errors without crashing the whole app.

### 6. Result Analysis

The `result_analyst` node turns the raw execution result into a user-facing answer. It is instructed to use only the execution output as the source of truth and avoid unsupported claims.

It returns an `AnalystResponse` containing:

- `answer`: final textual explanation.
- `visualization`: whether the result supports useful visualization.

### 7. Plot Building

If visualizations are enabled and the analysis response says a visualization is useful, the graph routes to `plot_builder`.

The plotting agent returns an `AllPlots` object with one or more chart specifications. `src/plotfunc.py` then maps those specifications to Plotly figures.

Supported chart types:

- `bar`
- `line`
- `pie`

## Project Structure

```text
.
├── README.md
├── data_context.txt
├── pyproject.toml
├── uv.lock
├── prompts
│   ├── analyst_prompt.yaml
│   ├── audit_prompt.yaml
│   ├── dev_prompt.yaml
│   ├── intent_prompt.yaml
│   └── plot_analyst.yaml
└── src
    ├── Makefile
    ├── agents.py
    ├── chainlit.md
    ├── config.py
    ├── excuter.py
    ├── graph.py
    ├── inference.py
    ├── logger.py
    ├── models.py
    ├── nodes.py
    ├── plotfunc.py
    ├── public
    │   ├── products_perf.svg
    │   ├── regional_perf.svg
    │   └── sales.svg
    ├── state.py
    └── utils.py
```

## Technology Stack

- Python 3.13+
- Chainlit for the chat interface.
- LangGraph for workflow orchestration.
- LangChain for prompt and model composition.
- Groq-hosted `openai/gpt-oss-120b` chat model.
- Pydantic for structured LLM outputs.
- PostgreSQL through `psycopg`.
- pandas for tabular result handling.
- Plotly for interactive visualizations.
- uv for dependency management.
- Rich for local logging.

## Data Model

The agent is configured for a sales analytics database covering 2023 through 2025.

### Tables

#### `sales`

Contains individual sales transactions.

Key columns:

- `orderid`
- `customerid`
- `productid`
- `orderdate`
- `quantity`
- `revenue`
- `cogs`

#### `products`

Contains product metadata.

Key columns:

- `productid`
- `productname`
- `productcategory`
- `price`
- `base_cost`

#### `customers`

Contains customer and geographic information.

Key columns:

- `customerid`
- `region`
- `customerjoindate`

### Relationships

```sql
sales.customerid = customers.customerid
sales.productid = products.productid
```

### Common Metrics

| Metric | Definition |
| --- | --- |
| Total revenue | `SUM(revenue)` |
| Total COGS | `SUM(cogs)` |
| Total profit | `SUM(revenue - cogs)` |
| Total quantity sold | `SUM(quantity)` |
| Average revenue | `AVG(revenue)` |

### Data Quality Notes

- `sales.customerid` contains missing values.
- `sales.revenue` contains missing values.
- Transactions without `customerid` cannot be mapped to a customer region.
- Revenue-based metrics should handle null revenue values appropriately.

## Requirements

Before running the project, make sure you have:

- Python 3.13 or newer.
- uv installed.
- Access to a PostgreSQL database matching the schema in `data_context.txt`.
- A valid database connection string.
- Credentials required by the configured LangChain/Groq model provider.

## Installation

From the repository root:

```bash
uv sync
```

This installs the dependencies defined in `pyproject.toml` and locked in `uv.lock`.

To activate the virtual environment:

```bash
source .venv/bin/activate
```

You can also use the Makefile inside `src`:

```bash
cd src
make install
```

## Environment Configuration

Create a `.env` file in the project root.

Required:

```env
CONNECTION_STRING=postgresql://username:password@host:port/database
```

The LLM is initialized with:

```python
init_chat_model("groq:openai/gpt-oss-120b")
```

Depending on your local LangChain/Groq configuration, you may also need to provide the appropriate model provider API key in `.env`, such as:

```env
GROQ_API_KEY=your_api_key_here
```

Do not commit `.env` to version control. The project already ignores it in `.gitignore`.

## Running the Application

The current app imports local modules such as `models`, `graph`, and `plotfunc` directly from the `src` directory. The simplest way to run it is from inside `src`.

```bash
cd src
chainlit run inference.py
```

For auto-reload during development:

```bash
cd src
chainlit run inference.py -w
```

Or use the Makefile:

```bash
cd src
make run
```

Development mode with reload:

```bash
cd src
make run-w
```

After startup, Chainlit will print the local URL for the web interface.

## Using the Assistant

When the app opens, users can either type a custom analytics question or choose one of the starter prompts:

- Sales Summary
- Product Performance
- Regional Performance

Example questions:

```text
Give me a sales performance summary for 2025, including total revenue, total COGS, total profit, and total quantity sold. Compare the results with 2024 and highlight the main changes.
```

```text
Analyze product performance for 2025. Show the top 5 products by total revenue, their total quantity sold and profit, and identify which products performed the best overall.
```

```text
Analyze sales performance by region for 2025. Show total revenue, total COGS, total profit, and quantity sold for each region, then identify the strongest and weakest performing regions.
```

If the request is ambiguous, the assistant asks one clarification question before generating SQL.

## Configuration

### Chainlit Settings

The chat UI exposes:

| Setting | Type | Purpose |
| --- | --- | --- |
| `Max_retries` | Slider | Intended maximum number of retries. |
| `Generate visualizations` | Switch | Enables or disables automatic Plotly charts. |

### Agent Configuration

`src/config.py` currently defines:

```python
CONFIDENCE_THRESHOLD = 0.60
```

This can be used as a threshold for intent confidence logic if confidence scoring is added to the intent model.

## Prompt System

Prompts live in the `prompts` directory and are loaded by `src/utils.py`.

| Prompt | Role |
| --- | --- |
| `intent_prompt.yaml` | Classifies requests and produces analytical intent. |
| `dev_prompt.yaml` | Generates PostgreSQL SQL from validated intent. |
| `audit_prompt.yaml` | Audits generated SQL for safety and correctness. |
| `analyst_prompt.yaml` | Explains execution results to the user. |
| `plot_analyst.yaml` | Recommends visualization specifications. |

Each prompt is paired with a Pydantic model in `src/models.py`, forcing the LLM to return structured output that the graph can route and process.

## Visualization System

Visualization is a two-step process:

1. `plot_builder` asks the plotting LLM to recommend chart specifications based on the returned columns, rows, and analytical intent.
2. `Get_Plots()` converts those specifications into Plotly figures.

The plot registry is defined in `src/plotfunc.py`:

```python
PLOT_REGISTRY = {
    "bar": create_barchart,
    "line": create_line,
    "pie": create_pie,
}
```

Each plot uses the `simple_white` Plotly template.

## Development Notes

### State Management

`AgentState` is a LangGraph `TypedDict` that carries:

- Conversation messages.
- Intent histories.
- Generated SQL.
- Audit result.
- Execution result.
- Final analytical response.
- Plot settings.
- Generated plot specifications.

Message and intent history are merged using reducer functions in `src/utils.py`.

### Checkpointing

The graph uses `InMemorySaver`, which keeps state in memory while the app process is running. This is suitable for local development, but production deployments should use a persistent checkpointer if conversation continuity matters after restarts.

### Logging

The app uses Rich logging through `src/logger.py`. Nodes log when each major step starts, which makes local graph execution easier to follow.

### Cleaning Local Cache Files

From inside `src`:

```bash
make clean
```

This removes Python and pytest cache folders.

## Troubleshooting

### `CONNECTION_STRING` is missing or invalid

If the database connection fails, confirm that `.env` exists in the project root and contains a valid PostgreSQL connection string:

```env
CONNECTION_STRING=postgresql://username:password@host:port/database
```

### Model authentication errors

If the LLM fails to initialize or invoke, confirm that the required model provider credentials are available in `.env`.

For the current Groq model configuration, that usually means setting:

```env
GROQ_API_KEY=your_api_key_here
```

### Import errors when running Chainlit

Run Chainlit from inside the `src` directory:

```bash
cd src
chainlit run inference.py
```

The source files currently use direct imports such as:

```python
from models import Message
from graph import Agent
```

Running from `src` ensures those modules are on the Python import path.

### No charts appear

Charts are returned only when all of the following are true:

- `Generate visualizations` is enabled in Chainlit settings.
- The result analyst marks the response as visualizable.
- The plot builder returns at least one valid plot specification.
- The SQL execution result contains suitable dimensions and numeric measures.

### Query returns an error

The SQL executor catches database exceptions and stores the error in `ExecutionState.error`. Check the terminal logs and verify:

- The database schema matches `data_context.txt`.
- Column names are lowercase.
- The generated SQL uses PostgreSQL syntax.
- The database user has read access to the relevant tables.

## Roadmap Ideas

Potential improvements:

- Add persistent LangGraph checkpointing for production use.
- Add automated tests for routing, SQL audit behavior, and plotting.
- Enforce max retry behavior in the graph state.
- Add an explicit `confidence` field to `IntentState` if prompt-level confidence should be used.
- Rename `src/excuter.py` to `src/executor.py` for clarity.
- Convert source imports into package-relative imports.
- Add a read-only SQL guard at execution time in addition to the LLM audit.
- Add support for more chart types and true pie chart rendering.
- Add deployment documentation for Docker or a cloud hosting target.

## License

No license file is currently included. Add a license before distributing or publishing the project.
