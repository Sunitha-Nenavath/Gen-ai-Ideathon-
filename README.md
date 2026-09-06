# ☕ Coffee Barista AI Agent

A customer-facing AI Barista Agent built using **Google ADK, Gemini, Python, and Streamlit**.

The agent helps customers discover drinks and pastries from a predefined coffee shop menu and provides recommendations based on preferences such as taste, temperature, dietary requirements, and allergens.

## 🚀 Live Demo

https://dcqiykrusdwbwtvajaosnb.streamlit.app/

## ✨ Features

- 🤖 AI-powered coffee shop assistant
- ☕ Drink and pastry recommendations
- 📋 Menu-grounded responses using `menu.json`
- 🚫 Prevents recommendations for unavailable menu items
- 🌱 Dairy-free and vegan recommendations
- ⚠️ Allergen-aware recommendations
- 💬 Conversational Streamlit interface
- 🔎 Retrieval-Augmented Generation (RAG) approach
- ☁️ Deployed using Streamlit Community Cloud

## 🧠 How It Works

The application uses a simple RAG-style architecture:

1. The customer asks a question.
2. The AI Barista retrieves the coffee shop menu from `menu.json`.
3. The Gemini model processes the customer's preferences.
4. The agent recommends suitable items using only the available menu.
5. The response is displayed through the Streamlit interface.

## 🏗️ Project Structure

```text
coffee-barista-agent/
│
├── agent.py
├── app.py
├── menu.json
├── requirements.txt
└── README.md
