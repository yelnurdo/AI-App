import streamlit as st
import sqlite3
import json
from dotenv import load_dotenv
import os
from transformers import pipeline, Conversation

# Load environment variables
load_dotenv()

# Get the Hugging Face token from the environment variables
hf_token = os.getenv("HF_TOKEN")

# Initialize the SQLite database
conn = sqlite3.connect('fridge.db')
c = conn.cursor()

# File to store favorite recipes
favorites_file = "favorites.json"


# Function to load favorites
def load_favorites():
    if os.path.exists(favorites_file):
        with open(favorites_file, "r") as file:
            return json.load(file)
    return []


# Function to get all products from the fridge database
def get_all_products():
    c.execute('SELECT name, quantity FROM products')
    return c.fetchall()


# Load Hugging Face model
model_name = "HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1"
chatbot = pipeline("conversational", model=model_name, use_auth_token=hf_token)


# Function to analyze recipes and fridge items
def analyze_nutrition(favorites, fridge_items):
    favorite_recipes = "\n".join([f"Recipe: {item['recipe']}" for item in favorites])
    fridge_contents = "\n".join([f"{item[0]}: {item[1]}" for item in fridge_items])

    prompt = f"""
    You are a personal nutritionist. Analyze the following favorite recipes and the items in the fridge.
    Provide personalized nutritional advice based on the analysis.

    Favorite Recipes:
    {favorite_recipes}

    Fridge Contents:
    {fridge_contents}

    Nutritional Advice:
    """

    conversation = Conversation(prompt)
    response = chatbot(conversation)
    return response.generated_responses[-1]


# Streamlit UI
st.title("Personal Nutritionist Chat with AI")

# Load favorites and fridge items
favorites = load_favorites()
fridge_items = get_all_products()

# Display favorite recipes
st.subheader("Favorite Recipes")
if favorites:
    for favorite in favorites:
        st.write(f"**{favorite['name']}**")
        st.write(favorite['recipe'])
else:
    st.write("No favorite recipes found.")

# Display fridge contents
st.subheader("Fridge Contents")
if fridge_items:
    for item in fridge_items:
        st.write(f"{item[0]}: {item[1]}")
else:
    st.write("No items in the fridge.")

# Initialize conversation history
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = None

# Button to start the chat
if st.button("Start Chat"):
    if not favorites and not fridge_items:
        st.warning("Add favorite recipes and items in the fridge to get nutritional advice.")
    else:
        initial_response = analyze_nutrition(favorites, fridge_items)
        st.session_state['conversation'] = Conversation(initial_response)
        st.session_state['chat_history'] = [f"Nutritionist: {initial_response}"]
        st.success("Chat started! You can now ask questions.")

# Chat interface
if st.session_state['conversation']:
    user_input = st.text_input("You:", key="user_input")

    if user_input:
        st.session_state['conversation'].add_user_input(user_input)
        response = chatbot(st.session_state['conversation'])
        st.session_state['chat_history'].append(f"You: {user_input}")
        st.session_state['chat_history'].append(f"Nutritionist: {response.generated_responses[-1]}")
        st.session_state['conversation'] = response

    st.subheader("Chat History")
    for chat in st.session_state['chat_history']:
        st.write(chat)

# Close the database connection
conn.close()
