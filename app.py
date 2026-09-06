# app.py
import os
import json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

# Configure environment & API key fallback
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
elif "GEMINI_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

# Set page config for a premium look
st.set_page_config(
    page_title="☕ Coffee Shop - Barista Bot",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make the header sticky (adapts to light/dark themes)
st.markdown("""
<style>
    div[data-testid="element-container"]:has(.header-container),
    div.element-container:has(.header-container) {
        position: sticky;
        top: 2.875rem;
        z-index: 999;
        background-color: transparent;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# App Header (using inline styles for the permanent coffee theme look)
st.markdown("""
<div class="header-container" style="text-align: center; padding: 20px; background: linear-gradient(135deg, #8B5E3C, #6F4E37); color: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; color: white;">☕ ☕ Coffee Shop</h1>
    <p style="margin: 5px 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">Your friendly AI Barista is ready to help you find the perfect drink or pastry!</p>
</div>
""", unsafe_allow_html=True)

# Load Menu for the sidebar
try:
    with open("menu.json", "r") as f:
        menu_items = json.load(f)
except Exception as e:
    st.error(f"Error loading menu: {e}")
    menu_items = []

# Sidebar Menu & API Key Setup
with st.sidebar:
    st.markdown("## 🔑 API Key Setup")
    api_key_val = os.environ.get("GOOGLE_API_KEY", "")
    
    input_key = st.text_input(
        "Gemini API Key",
        value=api_key_val,
        type="password",
        help="Enter your Google Gemini API Key. Get one for free at https://aistudio.google.com/app/apikey",
        key="sidebar_api_key"
    )

    if input_key.strip():
        os.environ["GOOGLE_API_KEY"] = input_key.strip()
        st.success("🟢 API Key configured")
        if st.button("💾 Save Key to .env file"):
            try:
                with open(".env", "w") as f:
                    f.write(f"GOOGLE_API_KEY={input_key.strip()}\n")
                st.success("Saved API Key to `.env`!")
            except Exception as ex:
                st.error(f"Failed to save `.env`: {ex}")
    else:
        st.warning("⚠️ No API Key set.")
        st.markdown("[👉 Get a free Gemini API Key](https://aistudio.google.com/app/apikey)")

    st.markdown("---")
    st.markdown("## ☕ Coffee Shop Menu")
    st.markdown("Explore our offerings and ask the barista for recommendations.")
    st.markdown("---")

    for item in menu_items:
        with st.container(border=True):
            st.markdown(f"**{item['name']}**  •  **${item['price']:.2f}**")
            st.caption(item['description'])

            # Tags & Allergens as native badges
            tags = " ".join([f"`{t}`" for t in item.get("tags", [])])
            if tags:
                st.markdown(tags)

            allergens = ", ".join(item.get("allergens", []))
            if allergens:
                st.markdown(f"⚠️ *Allergens: {allergens}*")

# Chat Interface
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if "runner" not in st.session_state:
    from google.adk.runners import InMemoryRunner
    from agent import barista_agent
    st.session_state.runner = InMemoryRunner(agent=barista_agent)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to ☕ Coffee Shop! What can I get started for you today?"}
    ]

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask for recommendations (e.g., 'What dairy-free pastries do you have?')"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    with st.chat_message("assistant"):
        active_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not active_key or not active_key.strip():
            no_key_warning = (
                "⚠️ **No API key provided.**\n\n"
                "Please enter your **Gemini API Key** in the sidebar under **🔑 API Key Setup** to start chatting with the AI Barista.\n\n"
                "👉 Don't have an API key? You can generate one for free at [Google AI Studio](https://aistudio.google.com/app/apikey)."
            )
            st.warning(no_key_warning)
            st.session_state.messages.append({"role": "assistant", "content": no_key_warning})
        else:
            try:
                from google.genai import types
                from google.adk.runners import InMemoryRunner
                from agent import barista_agent

                # Ensure runner is created with agent
                if "runner" not in st.session_state:
                    st.session_state.runner = InMemoryRunner(agent=barista_agent)

                user_id = "default_user"
                session_id = st.session_state.session_id
                runner = st.session_state.runner

                # Ensure session exists
                if not runner.session_service.get_session(app_name=runner.app_name, user_id=user_id, session_id=session_id):
                    runner.session_service.create_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)

                # Format message content
                msg_content = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
                
                # Execute runner
                res_events = list(runner.run(user_id=user_id, session_id=session_id, new_message=msg_content))

                response_text = "".join([
                    part.text
                    for event in res_events
                    if event.content and event.content.parts
                    for part in event.content.parts
                    if part.text
                ])

                if not response_text:
                    response_text = "I'm happy to help! Let me know what preferences or dietary restrictions you have."

                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                err_str = str(e)
                if "API key" in err_str or "API_KEY" in err_str or "401" in err_str or "unauthorized" in err_str.lower():
                    api_error_text = (
                        "🔑 **API Key Error**\n\n"
                        f"{err_str}\n\n"
                        "Please verify that your Gemini API Key is valid and entered correctly in the sidebar under **🔑 API Key Setup**.\n\n"
                        "👉 Get or create a key at [Google AI Studio](https://aistudio.google.com/app/apikey)."
                    )
                    st.error(api_error_text)
                    st.session_state.messages.append({"role": "assistant", "content": api_error_text})
                else:
                    st.error(f"Apologies, I ran into an error: {e}")
