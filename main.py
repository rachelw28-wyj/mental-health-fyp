import nlp_utils
import nltk
from sqlalchemy import text
from nltk.sentiment import SentimentIntensityAnalyzer
# Download the emotional dictionary behind the scenes
nltk.download('vader_lexicon', quiet=True)
# Initialize the VADER engine
sia = SentimentIntensityAnalyzer()
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db
from typing import List
from passlib.context import CryptContext
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# --- INITIALIZE GEMINI API ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not found in .env file! Fallback will fail.")

# Ensure database tables exist
models.Base.metadata.create_all(bind=engine)

# Set up the password hashing engine
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Checks if a plain password matches the scrambled hash in the database"""
    return pwd_context.verify(plain_password, hashed_password)

app = FastAPI(
    title="AI Chatbot for Mental Health Therapy",
    description="Backend API for FYP Part 2",
    version="1.0.0"
)

# Tell FastAPI to allow the browser to read files inside the "static" folder
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
@app.get("/index")
@app.get("/index")
async def index_page():
    return FileResponse("templates/index.html")

@app.get("/login")
async def login_page():
    return FileResponse("templates/login.html")

@app.get("/chat")
async def chat_page():
    return FileResponse("templates/chat.html")

@app.get("/history")
async def view_history_page():
    return FileResponse("templates/history.html")

@app.get("/therapist_index")
async def therapist_index_page():
    return FileResponse("templates/therapist_index.html")

@app.get("/mood")
async def mood_page():
    return FileResponse("templates/mood.html")

@app.get("/journal_page")
async def journal_page():
    return FileResponse("templates/journal.html")

@app.get("/userpage")
async def user_page():
    return FileResponse("templates/userpage.html")

@app.get("/therapist_history")
async def therapist_history_page():
    return FileResponse("templates/therapist_history.html")

@app.get("/therapist_dashboard")
async def therapist_dashboard_page():
    return FileResponse("templates/therapist_dashboard.html")

@app.get("/chat/{user_id}/summary")
async def generate_chat_summary(user_id: int, db: Session = Depends(get_db)):
    try:
        # --- 1. FETCH CHAT HISTORY ---
        history = db.execute(
            text("SELECT sender, message_text FROM chat_history WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).mappings().all() 
        
        if not history:
            return {"summary": "No conversation history found to summarize."}

        # --- 2. FORMAT TRANSCRIPT ---
        transcript = "Here is the conversation history between a Patient and an AI Therapy Assistant:\n\n"
        for msg in history:
            sender = "Patient" if msg['sender'] == 'User' else "Therapist AI"
            
            # Renamed variable to 'msg_text' to prevent conflict with SQLAlchemy's 'text()'
            msg_text = msg['message_text']           
            transcript += f"{sender}: {msg_text}\n"  

        # --- 3. CREATE GEMINI PROMPT ---
        prompt = f"""
        You are a professional clinical supervisor analyzing a therapy session transcript.
        Read the following conversation history and provide a concise, clinical summary of:
        1. The patient's primary concerns and current emotional state.
        2. Any notable triggers or high-risk language.
        3. The coping mechanisms or therapeutic techniques discussed.
        
        Keep the summary professional, objective, and format it cleanly using markdown. Keep it under 3 paragraphs.

        Transcript:
        {transcript}
        """

        # --- 4. GENERATE SUMMARY ---
        
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # Return the AI's response to the frontend
        return {"summary": response.text}

    except Exception as e:
        print(f"Error generating AI summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI summary.")
    
async def serve_frontend():
    """Serves the index.html file when someone visits the main URL"""
    return FileResponse("templates/index.html")

# --- HELPER FUNCTION: CRISIS DETECTION ---
def detect_crisis(text: str) -> bool:
    # Trigger keywords as defined in your FYP methodology
    risk_keywords = ["suicide", "kill", "die", "hurt", "end my life"]
    text_lower = text.lower()
    
    for word in risk_keywords:
        if word in text_lower:
            return True
    return False

# --- HELPER FUNCTION: GEMINI AI GENERATOR ---
def get_gemini_fallback(user_text: str) -> str:
    """Calls Gemini when the hardcoded CBT rules don't match."""
    try:
        system_prompt = """
        You are an AI Therapy Assistant designed for university students in Malaysia.
        You specialize in Cognitive Behavioral Therapy (CBT).
        Your tone must be empathetic, professional, warm, and conversational. 
        Keep your responses concise, ideally under 3-4 sentences. 
        Never officially diagnose a user.
        """
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt
        )
        response = model.generate_content(user_text)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I am here to listen. Could you tell me a bit more about how you are feeling?"

# --- HELPER FUNCTION: ADVANCED CBT GENERATOR ---
def generate_cbt_response(cleaned_tokens: list, original_text: str, sentiment: float, distortion: str) -> str:
    """
    Generates a targeted therapeutic response using CBT principles, 
    cognitive distortion detection, and NLP sentiment analysis.
    If no specific rules match, it passes the text to Gemini.
    """
    
  
    if distortion == "overgeneralization":
        return "I notice you used absolute words like 'always' or 'never'. In CBT, we call this all-or-nothing thinking. Is there ever a time when things didn't go terribly?"
    elif distortion == "catastrophizing":
        return "It sounds like you are anticipating the absolute worst-case scenario. Let's pause and reframe. What is a more realistic, middle-ground outcome here?"
    elif distortion == "should_statements":
        return "You are using a lot of 'shoulds' or 'musts', which can put unfair pressure on yourself. Try replacing 'I should' with 'I would prefer to' and see if that lessens the weight."

    
    if any(word in cleaned_tokens for word in ["stress", "anxious", "exam", "overwhelm", "panic", "tension"]):
        return "It sounds like you are carrying a lot of tension right now. Let's try a quick grounding exercise. Take a deep breath. Can you look around and name three things you can see, and two things you can touch?"
    
    elif any(word in cleaned_tokens for word in ["sad", "depress", "lonely", "cry", "heavy"]):
        return "I am so sorry you are feeling this heavy weight. It is completely valid to feel this way. Let's look for a small behavioral activation. What is one tiny, manageable thing you could do right now that might bring you a fraction of comfort?"
    
    elif any(word in cleaned_tokens for word in ["angry", "mad", "frustrate", "annoy"]):
        return "That sounds incredibly frustrating. When we feel anger, our bodies go into fight mode. Take a deep breath. What specifically triggered this intense feeling?"
    
   
    return get_gemini_fallback(original_text)

# --- CORE ENDPOINT: CHAT ---
@app.post("/chat", response_model=schemas.ChatMessageResponse)
def send_message(message: schemas.ChatMessageCreate, db: Session = Depends(get_db)):

    # VADER returns a 'compound' score from -1.0 (extreme negative) to +1.0 (extreme positive)
    calculated_sentiment = sia.polarity_scores(message.message_text)['compound']

    
    print(f"DEBUG - Calculated Sentiment: {calculated_sentiment}")

    
    user_msg = models.ChatHistory(
        user_id=message.user_id,
        sender='User',
        message_text=message.message_text,
        sentiment_score=calculated_sentiment
    )
    db.add(user_msg)
    db.commit()

   
    is_crisis = detect_crisis(message.message_text)

    if is_crisis:
       
        bot_response_text = "Are you okay? Please reach out for help immediately. Contact Talian HEAL at 15555 or Befrienders Malaysia at 03-76272929."
        
       
        crisis_log = models.CrisisEvent(
            user_id=message.user_id,
            trigger_word="System Detected Risk",
            risk_level="High",
            action_taken="Helpline Provided"
        )
        db.add(crisis_log)
    else:
       
        cleaned_words = nlp_utils.preprocess_text(message.message_text)

       
        detected_distortion = nlp_utils.detect_cognitive_distortion(message.message_text)
        
       
        bot_response_text = generate_cbt_response(
            cleaned_words, 
            message.message_text, 
            calculated_sentiment, 
            detected_distortion
        )
 
    bot_msg = models.ChatHistory(
        user_id=message.user_id,
        sender='Bot',
        message_text=bot_response_text
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)


    return bot_msg

# --- CORE ENDPOINT: AUTO-ANALYZE MOOD FROM CHAT ---
@app.post("/mood/auto-analyze/{user_id}")
def auto_analyze_mood(user_id: int, db: Session = Depends(get_db)):
    """Analyzes today's chat history to automatically generate a mood log."""
    today = datetime.now().date()
    
    # --- THE CRISIS OVERRIDE ---
    # 1. Check if the user triggered the Emergency Risk Protocol today
    all_crises = db.query(models.CrisisEvent).filter(models.CrisisEvent.user_id == user_id).all()
    crisis_today = [event for event in all_crises if event.timestamp.date() == today]
    
    if crisis_today:
        # BYPASS MATH: Force the lowest/most critical mood rating
        rating = 1
        emotion = "Critical / High Risk"
        final_note = "Auto-analyzed: Triggered by a High-Risk Crisis Event."
        
    else:
        # --- STANDARD MATH PROCESS ---
        # 2. Fetch all messages sent by this user
        history = db.query(models.ChatHistory).filter(
            models.ChatHistory.user_id == user_id,
            models.ChatHistory.sender == 'User'
        ).all()
        
        # 3. Filter for only TODAY's messages
        today_messages = [msg for msg in history if msg.timestamp.date() == today]
        
        if not today_messages:
            raise HTTPException(status_code=400, detail="No conversations found today to analyze.")
            
        # 4. Calculate average sentiment score from today's chats
        total_sentiment = sum(msg.sentiment_score for msg in today_messages if msg.sentiment_score is not None)
        avg_sentiment = total_sentiment / len(today_messages)
        
        # 5. Map the -1.0 to 1.0 sentiment score to a 1 to 5 mood rating
        if avg_sentiment <= -0.4:
            rating = 1
            emotion = "Sad / Angry"
        elif avg_sentiment <= -0.1:
            rating = 2
            emotion = "Anxious / Overwhelmed"
        elif avg_sentiment <= 0.2:
            rating = 3
            emotion = "Neutral"
        elif avg_sentiment <= 0.6:
            rating = 4
            emotion = "Happy / Content"
        else:
            rating = 5
            emotion = "Motivated / Energized"
            
        final_note = "Auto-analyzed by AI from today's conversation."
        
    # 6. Check if we already logged a mood today. If yes, update it. If no, create it.
    existing_log = db.query(models.MoodLog).filter(
        models.MoodLog.user_id == user_id,
        models.MoodLog.log_date == today
    ).first()
    
    if existing_log:
        existing_log.mood_rating = rating
        existing_log.primary_emotion = emotion
        existing_log.note = final_note
    else:
        new_log = models.MoodLog(
            user_id=user_id,
            mood_rating=rating,
            primary_emotion=emotion,
            note=final_note,
            log_date=today
        )
        db.add(new_log)
        
    db.commit()
    return {"status": "success", "rating": rating, "emotion": emotion}

# --- CORE ENDPOINT: MOOD TRACKING ---
@app.post("/mood", response_model=schemas.MoodLogResponse)
def log_mood(mood: schemas.MoodLogCreate, db: Session = Depends(get_db)):
    
    # 1. Package the incoming data into your SQLAlchemy model
    new_mood_log = models.MoodLog(
        user_id=mood.user_id,
        mood_rating=mood.mood_rating,
        primary_emotion=mood.primary_emotion,
        note=mood.note,
        log_date=mood.log_date
    )
    
    # 2. Save it to the database
    db.add(new_mood_log)
    db.commit()
    db.refresh(new_mood_log)
    
    # 3. Return the saved record
    return new_mood_log

# --- CORE ENDPOINT: GET CHAT HISTORY ---
@app.get("/chat/{user_id}", response_model=List[schemas.ChatMessageResponse])
def get_chat_history(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all past messages for a specific user, sorted by oldest to newest.
    """
    # Query the database for all messages matching the user_id
    history = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == user_id
    ).order_by(models.ChatHistory.timestamp.asc()).all()
    
    return history

# --- CORE ENDPOINT: GET MOOD HISTORY ---
@app.get("/mood/{user_id}", response_model=List[schemas.MoodLogResponse])
def get_mood_history(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all past mood logs for a specific user, sorted by newest to oldest.
    """
    # Query the database for all mood logs matching the user_id
    moods = db.query(models.MoodLog).filter(
        models.MoodLog.user_id == user_id
    ).order_by(models.MoodLog.log_date.desc()).all()
    
    return moods

# --- CORE ENDPOINT: CREATE JOURNAL ENTRY ---
@app.post("/journal", response_model=schemas.JournalEntryResponse)
def create_journal_entry(entry: schemas.JournalEntryCreate, db: Session = Depends(get_db)):
    """
    Saves a new free-text journal entry to the database.
    """
    new_entry = models.JournalEntry(
        user_id=entry.user_id,
        title=entry.title,
        content=entry.content
    )
    
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    
    return new_entry

# --- CORE ENDPOINT: GET JOURNAL ENTRIES ---
@app.get("/journal/{user_id}", response_model=List[schemas.JournalEntryResponse])
def get_journal_entries(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all past journal entries for a user, sorted by newest to oldest.
    """
    entries = db.query(models.JournalEntry).filter(
        models.JournalEntry.user_id == user_id
    ).order_by(models.JournalEntry.created_at.desc()).all()
    
    return entries

# --- CORE ENDPOINT: USER REGISTRATION ---
@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user account with a securely hashed password.
    """
    # 1. Check if the email or username is already taken
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    
    if db_user:
        # If they exist, throw a 400 Bad Request error
        raise HTTPException(status_code=400, detail="Email or username already registered")

    # 2. Scramble the password securely
    hashed_password = get_password_hash(user.password)

    # 3. Package the data into our SQLAlchemy model
    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    
    # 4. Save to the MySQL database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# --- CORE ENDPOINT: USER LOGIN ---
@app.post("/login", response_model=schemas.UserResponse)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Verifies a user's email and password to log them into the system.
    """
    # 1. Search the database for the email they typed in
    user = db.query(models.User).filter(
        models.User.email == user_credentials.email
    ).first()
    
    # 2. If the email doesn't exist, OR the passwords don't match, reject them
    # We use a 401 Unauthorized status code for failed logins
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # 3. If everything matches perfectly, return their user profile!
    return user

# --- PROFESSIONAL ENDPOINTS: THERAPIST DASHBOARD ---

@app.get("/therapist/patients", response_model=List[schemas.UserResponse])
def get_all_patients(db: Session = Depends(get_db)):
    """
    Retrieves a list of all users who are registered as 'Patient'.
    """
    patients = db.query(models.User).filter(models.User.role == 'Patient').all()
    return patients

@app.get("/therapist/patient/{user_id}/report")
def get_patient_report(user_id: int, db: Session = Depends(get_db)):
    """
    Gathers a comprehensive clinical report for a specific patient, 
    including recent moods, journals, and any flagged crisis events.
    """
    # 1. Verify the patient exists
    patient = db.query(models.User).filter(
        models.User.user_id == user_id, 
        models.User.role == 'Patient'
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 2. Fetch the patient's data (limiting to recent entries to keep the dashboard fast)
    moods = db.query(models.MoodLog).filter(
        models.MoodLog.user_id == user_id
    ).order_by(models.MoodLog.log_date.desc()).limit(14).all() # Last 14 days of moods
    
    journals = db.query(models.JournalEntry).filter(
        models.JournalEntry.user_id == user_id
    ).order_by(models.JournalEntry.created_at.desc()).limit(10).all() # Last 10 journals
    
    crises = db.query(models.CrisisEvent).filter(
        models.CrisisEvent.user_id == user_id
    ).order_by(models.CrisisEvent.timestamp.desc()).all() # All crisis events
    
    # 3. Package everything into a single, clean JSON response
    return {
        "patient_info": {
            "username": patient.username, 
            "email": patient.email, 
            "joined": patient.created_at
        },
        "recent_moods": moods,
        "recent_journals": journals,
        "crisis_events": crises
    }