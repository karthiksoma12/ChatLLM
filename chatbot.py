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
            st.experimental_rerun()
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

# --- Main App ---
def main_app():
    st.set_page_config(page_title="Airbnb Q&A", layout="centered")
    st.title("🏡 Airbnb Listing Q&A")

    description = st.text_area("Paste the Airbnb listing description here:", height=300)

    if description.strip():
        st.session_state["context"] = description.strip()

    if "context" in st.session_state:
        question = st.text_input("Ask a question about the listing:")

        if st.button("Get Answer"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Answering..."):
                    answer = ask_together_ai(question, st.session_state["context"])
                st.markdown(f"**Answer:** {answer}")

# --- Auth Flow ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_page()
else:
    main_app()
