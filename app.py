import streamlit as st

from src.ai.chat.main import chat
from src.ai.web_researcher.research_flow import stream as web_researcher
from src.ai.interview_simulation.flow import stream as interview_simulation

# 1. Page Configuration
st.set_page_config(page_title="Multi-Module Chatbot", page_icon="💬", layout="wide")

# 2. Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sidebar Configuration
st.sidebar.title("⚙️ Control Panel")
st.sidebar.markdown("Select a module method to process your chat prompts.")

# Map radio choices to your actual Python functions
module_mapping = {
    chat: { "name": "chat", "show_free_text": True, "stream": False },
    web_researcher: { "name": "web researcher", "show_free_text": True, "stream": True }, 
    interview_simulation: { "name": "interview simulation", "show_free_text": False, "stream": True }
}

selected_mode = st.sidebar.radio(
    "Choose Agent:",
    options=list(module_mapping.keys()),
    format_func=lambda k: f"{module_mapping[k]['name']}"
)
current_mode = module_mapping[selected_mode]["name"]
if "previous_mode" not in st.session_state:
    st.session_state.previous_mode = current_mode
elif st.session_state.previous_mode != current_mode:
    st.session_state.messages = []
    st.session_state.previous_mode = current_mode

# Optional sidebar button to clear chat
if st.sidebar.button("Clear Conversation History", type="primary"):
    st.session_state.messages = []
    st.rerun()

# 4. Display Existing Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle New User Input
if module_mapping[selected_mode]["show_free_text"]:
    user_prompt = st.chat_input("Type your message here...")
else:
    user_prompt = "Start" if st.button("Start") else None

if user_prompt:
    
    # Render user message instantly
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    # Save user message to history
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # Fetch the corresponding backend method dynamically based on the radio button
    active_method = selected_mode
    
    # Generate response using the selected method
    with st.chat_message("assistant"):
        if module_mapping[selected_mode]["stream"] == False:
            with st.spinner(f"Running {selected_mode}..."):
                response = active_method(st.session_state.messages)
            st.markdown(response)
        else:
            progress = st.container()
            response = st.write_stream(
                active_method(
                    user_prompt,
                    on_progress=lambda message: progress.caption(message),
                )
            )
            
    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
