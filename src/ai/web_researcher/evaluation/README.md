# Web Researcher Evaluation

This module evaluates saved researcher runs with a separate LLM judge. It does not run the researcher, search the web, or open cited URLs. The judge compares each saved answer with its recorded findings and, when a benchmark case matches, that case's expected facts and reference evidence.

## What It Evaluates

For each run, the judge returns scores from 1 (poor) to 5 (excellent) for:

- `groundedness`: whether answer claims are supported by the saved findings or reference evidence
- `coverage`: whether the answer addresses the question and expected facts, when supplied
- `citation_quality`: whether citations are traceable to the supplied findings; URLs are not fetched
- `reflection_quality`: whether the saved reflection state handles gaps, contradictions, and sufficiency appropriately
- `overall_score`: a holistic assessment, prioritizing correctness and evidence

The verdict also includes a rationale, unsupported claims, missing expected facts, and citation issues. A record is marked `passed` when `overall_score`, `groundedness`, and `coverage` are each at least 4. Citation and reflection scores are reported but do not affect this pass flag.

When a case has no matching benchmark entry, the judge still evaluates the answer against its recorded findings, but receives no expected facts or reference evidence. It is instructed not to infer support from a URL alone.

## Input Files

By default, the evaluator reads files in this directory:

- `research_results.jsonl`: saved runs from the researcher flow. Each record should include `question`, `answer`, `findings`, `source_urls`, and `reflection`.
- `evaluation_dataset.jsonl`: optional benchmark cases. Each case can include an `id`, `question`, `expected_facts`, and `search_results` containing reference evidence (`url` and `content`).

The loader accepts JSON Lines, a single JSON object, or an array of JSON objects. The dataset file may therefore be formatted as regular, pretty-printed JSON despite its `.jsonl` extension.

Benchmark cases are matched first by `evaluation_case_id` or `case_id` on a result, then by normalized question text. Keep benchmark and result questions identical for reliable matching.

Example benchmark case:

```json
{
	"id": "comparison-001",
	"question": "Compare X and Y on deployment cost.",
	"expected_facts": ["X costs ...", "Y costs ..."],
	"search_results": [
		{"url": "https://example.test/x", "content": "Reference evidence..."}
	]
}
```

## Run

The judge uses the project's Groq chat model. Set `GROQ_API_KEY`, then run from the repository root:

```powershell
$env:GROQ_API_KEY = "<your key>"
.\.venv\Scripts\python.exe -m src.ai.web_researcher.evaluation.main
```

Override any input or output path with command-line options:

```powershell
.\.venv\Scripts\python.exe -m src.ai.web_researcher.evaluation.main `
	--results src/ai/web_researcher/evaluation/research_results.jsonl `
	--dataset src/ai/web_researcher/evaluation/evaluation_dataset.jsonl `
	--output src/ai/web_researcher/evaluation/judge_results.jsonl
```

Each input record requires one judge model call. The default output is `judge_results.jsonl` in this directory. Results are appended, not overwritten; choose a new output path when you want a clean evaluation run. Re-running with the same output file evaluates all input records again and appends another verdict for each.

Each output line contains the input run's `timestamp` and `question`, the matched `case_id` when available, the structured `scores` and issue lists, plus the computed `passed` flag.
