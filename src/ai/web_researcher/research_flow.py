import argparse

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


def invoke(input: str) -> Any:
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
    
    print(f"graph response - {response["answer"]}")
    print(f"graph response - {response["answer_source"]}")

    return response["answer"]

def stream(input: str, on_progress: Callable[[str], None] | None = None) -> Iterator[str]:

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
    for event in compiled_flow.stream(graph_input, stream_mode="updates"):
        for node_name, state in event.items():
            if on_progress is not None and node_name in progress_labels:
                on_progress(progress_labels[node_name])
            if node_name == "answer" and state.get("answer"):
                answer_text = state["answer"]
                source_url = state.get("answer_source")
                if source_url:
                    answer_text += f"\n\nSource: <{source_url}>"
                yield answer_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="Research question")
    invoke(parser.parse_args().question)