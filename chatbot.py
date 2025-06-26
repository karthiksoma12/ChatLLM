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
            st.success("Login successful!")
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

# --- Phase 1: Paste Description UI ---
def description_input_screen():
    st.set_page_config(page_title="Airbnb Description Input", layout="centered")
    st.title("📋 Airbnb Listing Input")
    st.markdown("Paste the Airbnb listing description below to start chatting.")

    description = st.text_area("Listing Description", height=300)

    if st.button("Load Description"):
        if description.strip():
            st.session_state["context"] = description.strip()
            st.session_state["chat_history"] = []
            st.session_state["context_loaded"] = True
            st.rerun()
        else:
            st.warning("Please paste the listing description.")

# --- Phase 2: Chatbot UI ---
def chatbot_screen():
    st.set_page_config(page_title="Airbnb Chatbot", layout="centered")
    st.title("💬 Airbnb Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Chat History
    for chat in st.session_state["chat_history"]:
        st.markdown(f"**You:** {chat['question']}")
        st.markdown(f"**Bot:** {chat['answer']}")

    # Chat Input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask something about the listing...")
        submitted = st.form_submit_button("Send")
        if submitted and user_input.strip():
            with st.spinner("Thinking..."):
                answer = ask_together_ai(user_input.strip(), st.session_state["context"])
            st.session_state["chat_history"].append({"question": user_input.strip(), "answer": answer})
            st.rerun()

    # Option to restart
    if st.button("🔁 Reset"):
        for key in ["context", "context_loaded", "chat_history"]:
            st.session_state.pop(key, None)
        st.rerun()

# --- Auth & Flow Control ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    login_page()
elif "context_loaded" in st.session_state and st.session_state["context_loaded"]:
    chatbot_screen()
else:
    description_input_screen()
