import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# Download required NLTK data behind the scenes
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# Initialize the NLP tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text: str) -> list:
    """
    Cleans and processes raw text for the AI chatbot engine.
    """
    # 1. Lowercase and remove punctuation (keeps only letters and spaces)
    text_clean = re.sub(r'[^\w\s]', '', text.lower())
    
    # 2. Tokenize (split the sentence into individual words)
    tokens = word_tokenize(text_clean)
    
    # 3. Remove stop words and lemmatize (convert to base root words)
    # E.g., "running" becomes "run", "am" becomes "be"
    final_tokens = [
        lemmatizer.lemmatize(word) 
        for word in tokens 
        if word not in stop_words
    ]
    
    return final_tokens

def detect_cognitive_distortion(text: str):
    """
    Scans raw text for common CBT cognitive distortions (thinking traps).
    """
    text_lower = text.lower()
    
    # 1. All-or-Nothing / Overgeneralization
    if any(word in text_lower for word in ["always", "never", "everyone", "nobody", "total failure", "ruined everything"]):
        return "overgeneralization"
    
    # 2. Catastrophizing
    if any(word in text_lower for word in ["terrible", "disaster", "end of the world", "worst", "hopeless"]):
        return "catastrophizing"
        
    # 3. "Should" Statements (Unfair expectations)
    if any(word in text_lower for word in ["should have", "must", "supposed to", "have to be"]):
        return "should_statements"
        
    return None