import argparse

from langgraph.graph import StateGraph, START, END
from collections.abc import Callable, Iterator
from typing import Any

from src.ai.interview_simulation.agents import (
    MAX_REFLECTION_ITERATIONS,
    interviewee,
    interviewer,
    evaluator,
)

from src.ai.interview_simulation.schema import State


print("init graph")

# builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
my_flow = StateGraph(State)

my_flow.add_node("interviewer", interviewer)
my_flow.add_node("interviewee", interviewee)
my_flow.add_node("evaluator", evaluator)

my_flow.add_edge(START, "interviewer")
my_flow.add_edge("interviewer", "interviewee")
# my_flow.add_edge("interviewee", "evaluator")

def should_route_after_interviewee(state: State) -> str:
    iteration = state.get("iteration", 0) if isinstance(state, dict) else getattr(state, "iteration", 0)
    return "evaluator" if iteration >= MAX_REFLECTION_ITERATIONS else "interviewer"

my_flow.add_conditional_edges(
    "interviewee",
    should_route_after_interviewee,
    {"evaluator": "evaluator", "interviewer": "interviewer"},
)
my_flow.add_edge("evaluator", END)

print("compiling graph")

# compiled_graph = graph_builder.compile(checkpointer, cache, store, interrupt_before, interrupt_after, debug, name)
compiled_flow = my_flow.compile()


def invoke(input: str) -> Any:
    graph_input = { 
        "messages": [
        ]
    }

    print("invoking graph")

    # compiled_graph.invoke(input, config, context, interrupt_before, interrupt_after)
    response = compiled_flow.invoke(graph_input)
    
    print(f"graph response - {response["gaps"]}")
    print(f"graph response - {response["summary"]}")

    return response["summary"]

def stream(input: str, on_progress: Callable[[str], None] | None = None) -> Iterator[str]:

    graph_input = { 
        "messages": [
        ]
    }

    print("invoking graph")
    progress_labels = {
        "interviewer": "Asking interview questions",
        "interviewee": "Responding to interview questions",
        "evaluator": "Evaluating the interview",
    }
    for event in compiled_flow.stream(graph_input, stream_mode="updates"):
        for node_name, state in event.items():
            if on_progress is not None and node_name in progress_labels:
                on_progress(progress_labels[node_name])
            if node_name in {"interviewer", "interviewee"}:
                messages = state.get("messages", [])
                if messages:
                    message = messages[-1]
                    content = (
                        message.get("content", "")
                        if isinstance(message, dict)
                        else getattr(message, "content", str(message))
                    )
                    if content:
                        yield f"**{progress_labels[node_name]}**\n\n{content}\n\n"
            elif node_name == "evaluator" and state.get("summary"):
                answer_text = f"**Evaluation**\n\n{state['summary']}"
                gaps = state.get("gaps")
                if gaps:
                    answer_text += "\n\n**Gaps**\n\n" + "\n".join(
                        f"- {gap}" for gap in gaps
                    )
                yield answer_text


if __name__ == "__main__":
    invoke("start")