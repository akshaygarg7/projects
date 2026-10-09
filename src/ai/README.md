# AI Projects

An experimental collection of AI applications and agent workflows. 

## Setup

The project requires Python 3.14 or newer and uses `uv` to manage Python and project dependencies.

1. Install `uv` on Windows from PowerShell:

	```powershell
	winget install --id astral-sh.uv -e
	```

	Alternatively, follow the installation instructions at [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/).

2. From the repository root, install Python 3.14 and the project dependencies:

	```sh
	uv python install 3.14
	uv sync
	```

	`uv sync` creates the project environment and installs the dependencies declared in `pyproject.toml`.

3. Create a `.env` file in the repository root with the API keys used by the app:

	```dotenv
	GEMINI_API_KEY = your_gemini_api_key
	GROQ_API_KEY=your_groq_api_key
	OPENAI_API_KEY = your_openai_api_key
	MODEL_PROVIDER = "groq"

	TAVILY_API_KEY=your_tavily_api_key

	LANGSMITH_TRACING=true
	LANGSMITH_ENDPOINT=
	LANGSMITH_API_KEY=
	LANGSMITH_PROJECT=my-first-agent

	```

## Entry Point

Run the Streamlit chat interface from the repository root:

```sh
uv run --env-file .env streamlit run app.py
```
