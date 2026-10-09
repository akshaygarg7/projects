import unittest

from src.ai.common.llm.model_strategy import get_model_strategy


class ModelStrategyTests(unittest.TestCase):
    def test_returns_groq_strategy_by_default(self):
        strategy = get_model_strategy()
        self.assertEqual(strategy.name, "groq")

    def test_returns_gemini_strategy_when_selected(self):
        strategy = get_model_strategy("gemini")
        self.assertEqual(strategy.name, "gemini")


if __name__ == "__main__":
    unittest.main()
