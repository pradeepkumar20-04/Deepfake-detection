import os
import numpy as np
import tensorflow as tf
import cv2
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image, ImageChops, ImageEnhance
import matplotlib.pyplot as plt

# Load trained model
model_path = "tampering_detection_model_optimized.h5"
model = load_model(model_path)
print("Model loaded successfully.")

# Image Preprocessing
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# AI Model Prediction
def predict_tampering(img_path):
    img_array = preprocess_image(img_path)
    prediction = model.predict(img_array)[0][0]
    return "Tampered" if prediction > 0.5 else "Authentic"

# Error Level Analysis (ELA)
def error_level_analysis(image_path, quality=90):
    original = Image.open(image_path).convert('RGB')
    temp_path = "temp_image.jpg"
    original.save(temp_path, 'JPEG', quality=quality)
    compressed = Image.open(temp_path)
    ela_image = ImageChops.difference(original, compressed)
    enhancer = ImageEnhance.Contrast(ela_image)
    ela_image = enhancer.enhance(10)
    return np.array(ela_image)

# Noise Detection
def detect_noise(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    noise = cv2.Laplacian(img, cv2.CV_64F).var()
    return noise

# DCT Analysis
def dct_analysis(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    dct = cv2.dct(np.float32(img) / 255.0)
    return dct

# Comprehensive Analysis
def analyze_image(image_path):
    # AI Model Prediction
    ai_prediction = predict_tampering(image_path)

    # Forensic Analysis
    ela_result = error_level_analysis(image_path)
    noise_value = detect_noise(image_path)
    dct_result = dct_analysis(image_path)

    # Define a strict threshold
    noise_threshold = 100.0
    forensic_tampered = noise_value < noise_threshold

    # Final Decision
    final_prediction = "Tampered" if (ai_prediction == "Tampered" or forensic_tampered) else "Authentic"

    # Display results
    fig, axs = plt.subplots(1, 4, figsize=(15, 5))
    axs[0].imshow(ela_result)
    axs[0].set_title("ELA Analysis")

    axs[1].imshow(cv2.Canny(cv2.imread(image_path, cv2.IMREAD_GRAYSCALE), 30, 100), cmap='gray')
    axs[1].set_title("Edge Detection")

    axs[2].imshow(dct_result, cmap='gray')
    axs[2].set_title("DCT Analysis")

    axs[3].text(0.5, 0.5, final_prediction, fontsize=20,
                ha='center', va='center', color='red' if final_prediction == "Tampered" else 'green')
    axs[3].set_title("Final Prediction")
    axs[3].axis("off")

    plt.show()

    return final_prediction

# Test the function
image_path = "Au_ani_10142.jpg"  # Change this to your image path
result = analyze_image(image_path)
print("Final Decision:", result)
