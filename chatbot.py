import streamlit as st
from together import Together

# --- Setup Together API ---
together_api_key = st.secrets.get("TOGETHER_API_KEY")
client = Together(api_key=together_api_key)

# --- Login credentials from secrets.toml ---
VALID_USERS = dict(st.secrets["users"])

# --- Login Page ---
def login_page():
    st.title("🔐 Login to Chat Bot")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in VALID_USERS and VALID_USERS[username] == password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid username or password.")

# --- Together AI Q&A ---
def ask_together_ai(question, context):
    prompt = f"""
You are a helpful assistant. Based on the Airbnb listing details below, answer the user’s question.

Listing:
\"\"\"{context}\"\"\"

Question: {question}
Answer:"""
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Together AI Error: {e}"

# --- Phase 1: Input Description ---
def description_input_screen():
    st.set_page_config(page_title="Airbnb Description", layout="wide")
    st.title("📋 Paste Airbnb Description")

    description = st.text_area("Paste the Airbnb listing description below:", height=300)

    if st.button("Start Chat"):
        if description.strip():
            st.session_state["context"] = description.strip()
            st.session_state["chat_history"] = []
            st.session_state["context_loaded"] = True
            st.rerun()
        else:
            st.warning("Please enter a valid description.")

# --- Phase 2: Chat Interface ---
def chatbot_screen():
    st.set_page_config(page_title="Chatbot", layout="wide")
    st.markdown("<h1 style='text-align: center;'>💬 Airbnb Chatbot</h1>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # --- Chat Display ---
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state["chat_history"]:
            with st.chat_message("user"):
                st.markdown(chat["question"])
            with st.chat_message("assistant"):
                st.markdown(chat["answer"])

    # --- Input Bar (like ChatGPT) ---
    if prompt := st.chat_input("Ask something about the listing..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Assistant typing..."):
            answer = ask_together_ai(prompt, st.session_state["context"])
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state["chat_history"].append({"question": prompt, "answer": answer})

    # --- Reset Button ---
    st.sidebar.button("🔁 Restart", on_click=reset_app)

# --- Reset State ---
def reset_app():
    for key in ["context", "context_loaded", "chat_history"]:
        st.session_state.pop(key, None)
    st.rerun()

# --- Auth & Flow ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_page()
elif st.session_state.get("context_loaded"):
    chatbot_screen()
else:
    description_input_screen()
