import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load the hidden variables from the .env file
load_dotenv()

# Grab the Cloud Database URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    print("WARNING: DATABASE_URL not found in .env file!")

# Create the engine. The connect_args={"ssl": {}} tells Python to use 
# an encrypted connection, which Aiven strictly requires.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"ssl": {}}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to inject the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()