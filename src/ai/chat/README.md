# Chat Module

The chat module provides a conversational interface backed by the project's LLM provider adapters. The Streamlit app in the repository root supplies the UI and stores the conversation in session state; the chat module prepares that history and gets a response from the selected model.

## Design

- `main.py` normalizes message roles and content, manages long histories, adds the assistant system prompt, and invokes the selected model.
- `src/common/llm/model_strategy.py` selects the provider using `MODEL_PROVIDER`. It supports `groq` (the default) and `gemini`.

Messages are dictionaries with `role` and `content`, for example:

```python
{"role": "user", "content": "Hello"}
```

## Conversation History

When the chat contains more than five messages, the module asks the selected model to summarize the older messages. It then sends that summary together with the latest five messages when generating the response. At five messages or fewer, the full history is sent without a separate summarization call.

## Run

From the repository root, start the Streamlit app:

```powershell
uv run --env-file .env streamlit run app.py
```

To call the chat module directly from PowerShell:

```powershell
uv run --env-file .env python -c "from src.chat.main import chat; print(chat('What is artificial intelligence?'))"
```

The module also accepts existing history and a new user message:

```python
from src.ai.chat.main import chat

history = [
	{"role": "user", "content": "What is a neural network?"},
	{"role": "assistant", "content": "A model inspired by interconnected neurons."},
]
reply = chat("How is it trained?", history=history)
```