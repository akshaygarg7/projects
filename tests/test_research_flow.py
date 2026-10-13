import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ai.web_researcher import research_flow


class ResearchFlowStreamTests(unittest.TestCase):
    def test_stream_yields_answer_and_reports_node_progress(self):
        events = iter([
            {"planner": {"sub_queries": ["query"]}},
            {"answer": {"answer": "Final answer", "answer_source": "https://example.com"}},
        ])
        progress = []

        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir) / "results.jsonl"
            with patch.object(research_flow.compiled_flow, "stream", return_value=events):
                answer_chunks = list(
                    research_flow.stream(
                        "question", progress.append, results_path=results_path
                    )
                )

            record = json.loads(results_path.read_text(encoding="utf-8"))

        self.assertEqual(
            answer_chunks,
            ["Final answer\n\nSource: <https://example.com>"],
        )
        self.assertEqual(progress, ["Planning research", "Writing the answer"])
        self.assertEqual(record["question"], "question")
        self.assertEqual(record["answer"], "Final answer")
        self.assertEqual(record["source_urls"], ["https://example.com"])

    def test_invoke_appends_jsonl_records_with_research_state(self):
        response = {
            "answer": "Research answer",
            "answer_source": "https://answer.example",
            "findings_formatted": [
                {
                    "claim": "A fact",
                    "source_url": "https://finding.example",
                    "confidence": "high",
                }
            ],
            "iteration": 2,
            "sufficient": False,
            "gaps": ["A missing detail"],
            "contradictions": ["Conflicting values"],
            "follow_up_queries": ["verify value"],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir) / "results.jsonl"
            with patch.object(research_flow.compiled_flow, "invoke", return_value=response):
                research_flow.invoke("question", results_path=results_path)
                research_flow.invoke("question", results_path=results_path)

            records = [
                json.loads(line)
                for line in results_path.read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["answer"], "Research answer")
        self.assertEqual(records[0]["findings"][0]["claim"], "A fact")
        self.assertEqual(
            records[0]["source_urls"],
            ["https://finding.example", "https://answer.example"],
        )
        self.assertEqual(
            records[0]["reflection"],
            {
                "iteration": 2,
                "sufficient": False,
                "gaps": ["A missing detail"],
                "contradictions": ["Conflicting values"],
                "follow_up_queries": ["verify value"],
            },
        )


if __name__ == "__main__":
    unittest.main()