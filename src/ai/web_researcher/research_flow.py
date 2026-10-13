import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from langgraph.graph import StateGraph, START, END
from collections.abc import Callable, Iterator
from typing import Any

from src.ai.web_researcher.agents import (
    MAX_REFLECTION_ITERATIONS,
    answer,
    planner,
    reflect,
    searcher,
    synthesizer,
)

from src.ai.web_researcher.schema import ResearchState


DEFAULT_RESULTS_PATH = Path("research_results.jsonl")

print("init graph")

# builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
my_flow = StateGraph(ResearchState)

my_flow.add_node("planner", planner)
my_flow.add_node("searcher", searcher)
my_flow.add_node("synthesizer", synthesizer)
my_flow.add_node("reflect", reflect)
my_flow.add_node("answer", answer)

my_flow.add_edge(START, "planner")


my_flow.add_edge("planner", "searcher")
my_flow.add_edge("searcher", "synthesizer")
my_flow.add_edge("synthesizer", "reflect")
my_flow.add_conditional_edges(
    "reflect",
    lambda state: (
        "answer"
        if state.sufficient
        or state.iteration >= MAX_REFLECTION_ITERATIONS
        or not state.follow_up_queries
        else "searcher"
    ),
    {"searcher": "searcher", "answer": "answer"},
)
my_flow.add_edge("answer", END)

print("compiling graph")
# compiled_graph = graph_builder.compile(checkpointer, cache, store, interrupt_before, interrupt_after, debug, name)
compiled_flow = my_flow.compile()


def _append_result(response: dict, question: str, results_path: str | Path) -> None:
    findings = [
        finding.model_dump(mode="json")
        if hasattr(finding, "model_dump")
        else finding
        for finding in response.get("findings_formatted") or []
    ]
    source_urls = list(
        dict.fromkeys(
            [
                finding["source_url"]
                for finding in findings
                if isinstance(finding, dict) and finding.get("source_url")
            ]
            + ([response["answer_source"]] if response.get("answer_source") else [])
        )
    )
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "answer": response.get("answer"),
        "findings": findings,
        "source_urls": source_urls,
        "reflection": {
            "iteration": response.get("iteration"),
            "sufficient": response.get("sufficient"),
            "gaps": response.get("gaps", []),
            "contradictions": response.get("contradictions", []),
            "follow_up_queries": response.get("follow_up_queries", []),
        },
    }

    results_file = Path(results_path)
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with results_file.open("a", encoding="utf-8") as output_file:
        output_file.write(json.dumps(record, ensure_ascii=False) + "\n")


def invoke(input: str, results_path: str | Path = DEFAULT_RESULTS_PATH) -> Any:
    graph_input = { 
        "question": input,
        "messages": [
            {
                "role": "Human",
                "content": f"{input}"
             }
        ]
    }

    print("invoking graph")

    # compiled_graph.invoke(input, config, context, interrupt_before, interrupt_after)
    response = compiled_flow.invoke(graph_input)
    _append_result(response, input, results_path)
    
    print(f"graph response - {response["answer"]}")
    print(f"graph response - {response["answer_source"]}")

    return response["answer"]

def stream(
    input: str,
    on_progress: Callable[[str], None] | None = None,
    results_path: str | Path = DEFAULT_RESULTS_PATH,
) -> Iterator[str]:

    graph_input = { 
        "question": input,
        "messages": [
            {
                "role": "Human",
                "content": f"{input}"
             }
        ]
    }

    print("invoking graph")
    progress_labels = {
        "planner": "Planning research",
        "searcher": "Searching the web",
        "synthesizer": "Synthesizing findings",
        "reflect": "Checking research coverage",
        "answer": "Writing the answer",
    }
    final_state = {}
    for event in compiled_flow.stream(graph_input, stream_mode="updates"):
        for node_name, state in event.items():
            final_state.update(state)
            if on_progress is not None and node_name in progress_labels:
                on_progress(progress_labels[node_name])
            if node_name == "answer" and state.get("answer"):
                _append_result(final_state, input, results_path)
                answer_text = state["answer"]
                source_url = state.get("answer_source")
                if source_url:
                    answer_text += f"\n\nSource: <{source_url}>"
                yield answer_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="Research question")
    parser.add_argument(
        "--results-file",
        default=DEFAULT_RESULTS_PATH,
        type=Path,
        help="JSONL file to append research results to",
    )
    args = parser.parse_args()
    invoke(args.question, results_path=args.results_file)