import unittest
from unittest.mock import patch

from src.ai.web_researcher import research_flow


class ResearchFlowStreamTests(unittest.TestCase):
    def test_stream_yields_answer_and_reports_node_progress(self):
        events = iter([
            {"planner": {"sub_queries": ["query"]}},
            {"answer": {"answer": "Final answer", "answer_source": "https://example.com"}},
        ])
        progress = []

        with patch.object(research_flow.compiled_flow, "stream", return_value=events):
            answer_chunks = list(research_flow.stream("question", progress.append))

        self.assertEqual(
            answer_chunks,
            ["Final answer\n\nSource: <https://example.com>"],
        )
        self.assertEqual(progress, ["Planning research", "Writing the answer"])


if __name__ == "__main__":
    unittest.main()