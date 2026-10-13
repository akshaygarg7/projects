import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.ai.interview_simulation import agents
from src.ai.interview_simulation import flow


class InterviewSimulationStreamTests(unittest.TestCase):
    def test_stream_yields_each_node_output_and_reports_progress(self):
        events = iter([
            {"interviewer": {"messages": [{"role": "assistant", "content": "Tell me about yourself."}]}},
            {"interviewee": {"messages": [{"role": "assistant", "content": "I build software."}]}},
            {"evaluator": {"summary": "Clear response.", "gaps": ["Add measurable impact."]}},
        ])
        progress = []

        with patch.object(flow.compiled_flow, "stream", return_value=events):
            output = "".join(flow.stream("start", progress.append))

        self.assertIn("**Asking interview questions**", output)
        self.assertIn("Tell me about yourself.", output)
        self.assertIn("**Responding to interview questions**", output)
        self.assertIn("I build software.", output)
        self.assertIn("**Evaluation**", output)
        self.assertIn("Clear response.", output)
        self.assertIn("Add measurable impact.", output)
        self.assertEqual(
            progress,
            [
                "Asking interview questions",
                "Responding to interview questions",
                "Evaluating the interview",
            ],
        )

    def test_second_interviewer_call_uses_candidate_answer_for_follow_up(self):
        candidate_answer = "I would partition the data by customer ID."
        mock_agent = unittest.mock.Mock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "How would you handle a hot customer?"}]
        }
        state = SimpleNamespace(
            messages=[
                {"role": "assistant", "content": "Design a payment system."},
                {"role": "assistant", "content": candidate_answer},
            ]
        )

        with patch.object(agents, "create_agent", return_value=mock_agent):
            agents.interviewer(state, None, None)

        request = mock_agent.invoke.call_args.args[0]["messages"][0]["content"]
        self.assertIn(candidate_answer, request)
        self.assertIn("focused follow-up question", request)


if __name__ == "__main__":
    unittest.main()