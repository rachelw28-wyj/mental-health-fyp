import json
import os
import re

USERS_FILE = "users.json"

# Function to load user data
def load_users():
    try:
        if not os.path.exists(USERS_FILE):
            return {}
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

# Function to save user data
def save_users(users):
    try:
        with open(USERS_FILE, "w") as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        print(f"Error saving users: {e}")

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# Signup function
def signup(users, email, password, confirm_password, username):
    # Check if any of the fields are empty
    if not email or not password or not confirm_password or not username:
        return False, "All fields are required."
        
    if password != confirm_password:
        return False, "Passwords do not match."

    if email in users:
        return False, "User already exists. Please log in."
    users[email] = {"email": email, "password": password}
    save_users(users)
    return True, "Signup successful!"

# Login function
def login(users, email, password):
    if email in users and users[email]["password"] == password:
        return True, users[email]["username"]
    return False, "Invalid credentials."

def process_question(question):
    # Placeholder chatbot logic (replace with actual logic)
    if "hello" in question.lower():
        return "Hello! How can I help you today?"
    elif "pdf" in question.lower():
        return "This PDF contains useful information. Feel free to ask any specific questions!"
    return "I'm sorry, I don't understand the question."
    