import streamlit as st
from bs4 import BeautifulSoup
from together import Together

# --- Setup Together API ---
together_api_key = st.secrets.get("TOGETHER_API_KEY") # Add your Together API key here
client = Together(api_key=together_api_key)

# --- Simple login credentials ---
VALID_USERS = dict(st.secrets["users"])

# --- Login Page ---
def login_page():
    st.title("🔐 Login to Chat Bot")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in VALID_USERS and VALID_USERS[username] == password:
            st.session_state["authenticated"] = True
            st.success("Login successful! Please proceed.")
            st.rerun()
        else:
            st.error("Invalid username or password.")

# --- HTML Parsing Function ---
def parse_uploaded_html(uploaded_file):
    try:
        html_content = uploaded_file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        full_text = soup.get_text(separator="\n", strip=True)
        return full_text[:15000]  # limit to prevent token overflow
    except Exception as e:
        return f"HTML Parsing Error: {e}"

# --- Together AI ---
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
    st.set_page_config(page_title="Chat Bot", layout="centered")
    st.title("🏡 Chat Bot")

    uploaded_file = st.file_uploader("Upload a saved Airbnb listing HTML file:", type=["html", "htm"])

    if uploaded_file is not None:
        with st.spinner("Processing uploaded file..."):
            context = parse_uploaded_html(uploaded_file)
            if context.startswith("HTML Parsing Error"):
                st.error(context)
            else:
                st.session_state["context"] = context
                st.success("HTML content parsed and stored in memory.")

    if "context" in st.session_state:
        question = st.text_input("Ask a question about this listing:")

        if st.button("Get Answer"):
            if question.strip() == "":
                st.warning("Please enter a question.")
            else:
                with st.spinner("Answering..."):
                    answer = ask_together_ai(question, st.session_state["context"])
                st.markdown(f"**Answer:** {answer}")

# --- Control Flow ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_page()
else:
    main_app()
