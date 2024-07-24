from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base

# Define the database URL
DATABASE_URL = "postgresql://postgres:12345@localhost/test"

# Create an engine and sessionmaker
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional: Create tables if they don't exist
def create_database():
    Base.metadata.create_all(bind=engine)

