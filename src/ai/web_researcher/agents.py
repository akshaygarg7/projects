
from langchain.agents import create_agent

from src.ai.common.llm.model_strategy import get_model
from src.ai.web_researcher.schema import ResearchState, PlannerOutput, SynthesizeOutput, ReflectOutput, AnswerOutput
from src.ai.web_researcher.prompts import PROMPT_PLAN, PROMPT_SYNTHESIZE, PROMPT_REFLECT, PROMPT_ANSWER
from src.ai.common.tools.search import search

MAX_REFLECTION_ITERATIONS = 2

model = get_model().get_langchain_model()

# node_function(state, config, runtime) -> state
def planner(state, config, runtime) -> ResearchState:
    print(state.question)
    
    agent = create_agent(
        model=model,
        system_prompt=PROMPT_PLAN,
        response_format = PlannerOutput
    )

    input = {"messages": [{"role": "user", "content": state.question}]}

    node_response = agent.invoke(input)

    print(f"sub queries - {node_response["structured_response"].sub_queries}")

    return { "sub_queries": node_response["structured_response"].sub_queries }

def searcher(state, config, runtime) -> ResearchState:
    print(f"searcher node - iteration {state.iteration}")

    queries = state.follow_up_queries or [state.question]
    search_results = []
    for query in queries:
        result = search(query)["results"]
        print(f" {len(result)} search results for query '{query}'")
        search_results.extend(result)

    node_response = {
        "search_results": search_results,
        "iteration": state.iteration + 1,
        "follow_up_queries": [],
    }
    
    return node_response

def synthesizer(state, config, runtime):

    if not state.search_results:
        return {"findings_formatted": state.findings_formatted or []}
    
    system_prompt = PROMPT_SYNTHESIZE.format(query=state.question, url=state.search_results[0]["url"], scraped_content=state.search_results[0]["content"])

    agent = create_agent(
        model=model,
        system_prompt=system_prompt,
        response_format = SynthesizeOutput,
    )

    node_response = agent.invoke( {
            "messages": [
                {
                    "role": "user",
                    "content": "Synthesize the provided research content.",
                }
            ]
        })

    findings = list(state.findings_formatted or [])

    # Append the new findings to the existing list of findings
    findings.extend(node_response["structured_response"].findings)

    print(f"{len(findings)} findings after synthesis")
    return { "findings_formatted": findings }

def reflect(state, config, runtime) -> ResearchState:

    findings = "\n".join(
        f"- {finding.claim} (Source: {finding.source_url})"
        for finding in state.findings_formatted or []
    )
    system_prompt = PROMPT_REFLECT.format(
        original_query=state.question,
        iteration=state.iteration,
        max_iterations=MAX_REFLECTION_ITERATIONS,
        findings_formatted=findings,
    )
    agent = create_agent(
        model=model,
        system_prompt=system_prompt,
        response_format=ReflectOutput,
    )

    node_response = agent.invoke({
        "messages": [{"role": "user", "content": "Evaluate the research findings."}]
    })

    result = node_response["structured_response"]
    
    return {
        "sufficient": result.sufficient,
        "gaps": result.gaps,
        "contradictions": result.contradictions,
        "follow_up_queries": result.follow_up_queries,
    }

def answer(state, config, runtime):

    system_prompt = PROMPT_ANSWER.format(original_query=state.question, findings_formatted_with_numbered_sources=state.findings_formatted)
    agent = create_agent(
        model=model,
        system_prompt=system_prompt,
        response_format = AnswerOutput,
    )

    node_response = agent.invoke( {
            "messages": [
                {
                    "role": "user",
                    "content": "Generate answer.",
                }
            ]
        })

    strc_res =node_response["structured_response"]
    return { "answer": strc_res.answer , "answer_source": strc_res.source_url }
