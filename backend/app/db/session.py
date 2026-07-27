from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

# Setup SQLite Database for Audit Logs
SQLALCHEMY_DATABASE_URL = "sqlite:///./finshield.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables on startup
def init_db():
    Base.metadata.create_all(bind=engine)
