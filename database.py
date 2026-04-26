from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Define database URL for XAMPP (root user, no password)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/mental_health_db"

# 2. Create the SQLAlchemy engine (the bridge to MySQL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Create a SessionLocal class for database conversations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create a Base class for the data models
Base = declarative_base()

# 5. Dependency function to safely open/close database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()