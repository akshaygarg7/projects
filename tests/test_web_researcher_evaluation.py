import json
import tempfile
import unittest
from pathlib import Path

from src.ai.web_researcher.evaluation.main import JudgeVerdict, load_records, run_evaluation


class ResearchEvaluationTests(unittest.TestCase):
    def test_load_records_accepts_pretty_json_concatenated_objects_and_jsonl(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            pretty_json_path = Path(temp_dir) / "dataset.jsonl"
            pretty_json_path.write_text(
                '{\n  "question": "Q",\n  "expected_facts": ["fact"]\n}',
                encoding="utf-8",
            )
            concatenated_path = Path(temp_dir) / "concatenated.jsonl"
            concatenated_path.write_text(
                json.dumps({"question": "Q1"}, indent=2)
                + "\n"
                + json.dumps({"question": "Q2"}, indent=2),
                encoding="utf-8",
            )
            jsonl_path = Path(temp_dir) / "runs.jsonl"
            jsonl_path.write_text(
                '{"question": "Q1"}\n{"question": "Q2"}\n', encoding="utf-8"
            )

            self.assertEqual(load_records(pretty_json_path)[0]["question"], "Q")
            self.assertEqual(len(load_records(concatenated_path)), 2)
            self.assertEqual(len(load_records(jsonl_path)), 2)

    def test_run_evaluation_appends_structured_verdict(self):
        verdict = JudgeVerdict(
            groundedness=5,
            coverage=4,
            citation_quality=4,
            reflection_quality=4,
            overall_score=4,
            rationale="Supported and sufficiently complete.",
            unsupported_claims=[],
            missing_expected_facts=[],
            citation_issues=[],
        )

        class FakeJudge:
            def invoke(self, _input):
                return {"structured_response": verdict}

        def fake_agent_factory(**_kwargs):
            return FakeJudge()

        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir) / "research.jsonl"
            dataset_path = Path(temp_dir) / "dataset.json"
            output_path = Path(temp_dir) / "scores.jsonl"
            results_path.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-10-12T00:00:00Z",
                        "question": "What is Q?",
                        "answer": "Q is supported.",
                        "findings": [{"claim": "Q is supported.", "source_url": "https://example.test"}],
                        "source_urls": ["https://example.test"],
                        "reflection": {"sufficient": True},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            dataset_path.write_text(
                json.dumps(
                    {
                        "question": "What is Q?",
                        "expected_facts": ["Q is supported."],
                        "search_results": [],
                    }
                ),
                encoding="utf-8",
            )

            evaluation = run_evaluation(
                results_path,
                dataset_path,
                output_path,
                model=object(),
                agent_factory=fake_agent_factory,
            )

            saved_records = load_records(output_path)

        self.assertTrue(evaluation[0]["passed"])
        self.assertEqual(saved_records[0]["case_id"], None)
        self.assertEqual(saved_records[0]["scores"]["overall_score"], 4)


if __name__ == "__main__":
    unittest.main()