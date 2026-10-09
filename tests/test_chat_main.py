import unittest
from unittest.mock import patch

from src.ai.chat.main import _normalize_messages, chat


class ChatMainTests(unittest.TestCase):
    def test_normalize_messages_keeps_history_order(self):
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        result = _normalize_messages(history)

        self.assertEqual(result, [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ])

    def test_normalize_messages_accepts_single_prompt(self):
        result = _normalize_messages("What is AI?")

        self.assertEqual(result, [{"role": "user", "content": "What is AI?"}])

    @patch("src.chat.main.get_model")
    def test_chat_summarizes_history_beyond_five_messages(self, get_model):
        model = get_model.return_value
        model.invoke.side_effect = ["Earlier context", "Final answer"]
        history = [
            {"role": "user", "content": f"Message {index}"}
            for index in range(6)
        ]

        result = chat(history)

        self.assertEqual(result, "Final answer")
        self.assertEqual(model.invoke.call_count, 2)
        summary_input = model.invoke.call_args_list[0].args[0]
        self.assertIn("Message 0", summary_input[1]["content"])
        self.assertNotIn("Message 1", summary_input[1]["content"])
        final_input = model.invoke.call_args_list[1].args[0]
        self.assertEqual(final_input[1]["content"], "Summary of earlier conversation: Earlier context")
        self.assertEqual(final_input[2:], history[-5:])

    @patch("src.chat.main.get_model")
    def test_chat_does_not_summarize_five_or_fewer_messages(self, get_model):
        model = get_model.return_value
        model.invoke.return_value = "Final answer"
        history = [
            {"role": "user", "content": f"Message {index}"}
            for index in range(5)
        ]

        result = chat(history)

        self.assertEqual(result, "Final answer")
        model.invoke.assert_called_once()
        self.assertEqual(model.invoke.call_args.args[0][1:], history)


if __name__ == "__main__":
    unittest.main()
