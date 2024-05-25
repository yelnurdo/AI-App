import streamlit as st
import numpy as np
from PIL import Image
from transformers import pipeline, AutoImageProcessor, AutoModelForImageClassification
from dotenv import load_dotenv
import os

load_dotenv()

# Load the token from the .env file
token = os.getenv('HF_TOKEN')

# Load the first food classification model
model_name_v1 = "Kaludi/Food-Classification"
processor_v1 = AutoImageProcessor.from_pretrained(model_name_v1)
model_v1 = AutoModelForImageClassification.from_pretrained(model_name_v1)
food_classification_v1 = pipeline("image-classification", model=model_v1, feature_extractor=processor_v1)

# Load the second food classification model
model_name_v2 = "Kaludi/food-category-classification-v2.0"
processor_v2 = AutoImageProcessor.from_pretrained(model_name_v2, token=token)
model_v2 = AutoModelForImageClassification.from_pretrained(model_name_v2, token=token)
food_classification_v2 = pipeline("image-classification", model=model_v2, feature_extractor=processor_v2)

# Helper function to classify food items and retrieve ingredients
def classify_food_and_get_ingredients(image):
    results_v1 = food_classification_v1(image)
    results_v2 = food_classification_v2(image)

    classified_items_v1 = [result['label'] for result in results_v1]
    classified_items_v2 = [result['label'] for result in results_v2]

    # For simplicity, we assume the first model gives the name and the second model gives the ingredients
    food_name = classified_items_v1[0] if classified_items_v1 else "Unknown"
    ingredients = classified_items_v2 if classified_items_v2 else ["Ingredients not found"]

    return food_name, ingredients

# Streamlit App
st.title("Food Classification App")

# Upload an image for food classification
st.header("Upload an image to classify food items and get ingredients")
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    # Convert the image to a format compatible with the pipeline
    image_np = np.array(image)

    # Convert the numpy array back to a PIL image
    image_pil = Image.fromarray(image_np)

    # Classify food items and get ingredients
    food_name, ingredients = classify_food_and_get_ingredients(image_pil)
    st.write("Classified Food:", food_name)
    st.write("Ingredients:", ingredients)