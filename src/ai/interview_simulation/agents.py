
from langchain.agents import create_agent

from src.ai.common.llm.model_strategy import get_model
from src.ai.interview_simulation.schema import State, EvaluatorOutput
from src.ai.interview_simulation.prompts import PROMPT_INTERVIEWEE, PROMPT_INTERVIEWER, PROMPT_EVALUATOR


MAX_REFLECTION_ITERATIONS = 2

model = get_model().get_langchain_model()


def _format_transcript(messages) -> str:
    transcript = []
    for message in messages:
        if isinstance(message, dict):
            role = message.get("role", "unknown")
            content = message.get("content", "")
        else:
            role = {"human": "user", "ai": "assistant"}.get(
                getattr(message, "type", "unknown"), "unknown"
            )
            content = getattr(message, "content", str(message))
        transcript.append(f"{role}: {content}")
    return "\n".join(transcript)


def _message_content(message) -> str:
    if isinstance(message, dict):
        return message.get("content", "")
    return getattr(message, "content", str(message))


def interviewer(state, config, runtime) -> State:
    messages = list(state.messages or [])
    system_prompt = PROMPT_INTERVIEWER.format(chat_history=_format_transcript(messages))

    agent = create_agent(
        model=model,
        system_prompt=system_prompt,
    )

    if messages:
        latest_answer = _message_content(messages[-1])
        interviewer_request = (
            f"The candidate's latest answer was:\n{latest_answer}\n\n"
            "Ask one focused follow-up question based specifically on this answer."
        )
    else:
        interviewer_request = "Start the interview by presenting a distributed system design scenario."

    input = {"messages": [{"role": "user", "content": interviewer_request}]}

    node_response = agent.invoke(input)
    
    last_message = node_response.get("messages", [])[-1] if node_response.get("messages") else {"role": "assistant", "content": node_response.get("output") or str(node_response)}
    messages.append(last_message)

    print(last_message)

    return {"messages": messages}

def interviewee(state, config, runtime) -> State:
    messages = list(state.messages or [])

    system_prompt = PROMPT_INTERVIEWEE.format(chat_history=_format_transcript(messages))

    agent = create_agent(
        model=model,
        system_prompt=system_prompt,
    )
    
    node_response = agent.invoke(messages[-1])
    
    last_message = node_response.get("messages", [])[-1] if node_response.get("messages") else {"role": "assistant", "content": node_response.get("output") or str(node_response)}
    messages.append(last_message)
    print(last_message)


    
    return {"messages": messages, "iteration": state.iteration + 1}


def evaluator(state, config, runtime) -> State:

    system_prompt = PROMPT_EVALUATOR.format(transcript=_format_transcript(state.messages))

    agent = create_agent(
        model=model,
        system_prompt=system_prompt,
        response_format=EvaluatorOutput,
    )

    node_response = agent.invoke({
        "messages": [{"role": "user", "content": "Evaluate the interview transcript."}]
    })

    result = node_response["structured_response"]
    print(result)
    return {
        "gaps": result.gaps,
        "summary": result.summary,
    }
