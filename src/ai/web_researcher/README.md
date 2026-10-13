## Web Researcher Design

The web-researcher is built as LangGraph stateful workflow. 
Each node in the graph is an individual agent with specific responsibility.
Its shared state carries the question, search results, accumulated findings, reflection results, and final answer.


## HLD
<img src="Agent Architecture - Frame 1.jpg" alt="Architecture" width="500" height="500">


The workflow runs these steps:

1. **Planner** proposes focused search sub-queries.
2. **Searcher** searches Tavily. The initial search currently uses the original question; follow-up rounds use queries proposed by reflection.
3. **Synthesizer** extracts findings with source URLs. It currently synthesizes the first result in each search batch, retaining findings from earlier rounds.
4. **Reflector** evaluates whether the findings answer the question, identifies gaps or contradictions, and proposes follow-up queries when useful.
5. **Answerer** writes the final response from the collected findings, with source citations.

**Agent loop termination condition** - 
Reflection can route the workflow back to search. It stops when the findings are sufficient, there are no follow-up queries, or the iteration limit is reached.


## Calling the Workflow


### `invoke(question)`

`invoke` runs the workflow synchronously with `compiled_flow.invoke()`. It waits for the full research run, prints the final answer and selected source URL, and returns only the answer text. Each completed run is appended as one JSON object per line to `research_results.jsonl` in the current directory. Records include the question, answer, findings, source URLs, reflection state, and timestamp. Pass `results_path` to `invoke` or `stream` to choose another file:

```python
from src.ai.web_researcher.research_flow import invoke

answer = invoke(
	"What are the latest developments in battery recycling?",
	results_path="evaluation/research_results.jsonl",
)
print(answer)
```

### `stream(question, on_progress=None)`

`stream` is an iterator backed by `compiled_flow.stream(..., stream_mode="updates")`. As graph nodes finish, it calls the optional `on_progress` callback with labels such as `Searching the web` and `Synthesizing findings`. When the answer node finishes, it yields the completed answer with its source URL and appends the run to the same JSONL format:

```python
from src.ai.web_researcher.research_flow import stream

for text in stream("What are the latest developments in battery recycling?", on_progress=print):
	print(text, end="")
```

## Run the Web Researcher

Complete the setup steps mentioned in ReadMe at root directory.

Run the web-researcher in terminal

```sh
uv run --env-file .env python -m src.ai.web_researcher.research_flow "<your question>"
```
It will ask you to enter research topic in terminal itself.


Run the web-researcher in Streamlit UI

```sh
uv run --env-file .env streamlit run app.py
```

Once UI is up, select researcher in left menu, type research topic and hit enter. 
