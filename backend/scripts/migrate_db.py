import os
import pandas as pd
from sqlalchemy import create_engine
from app.db.models import Base, Transaction

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/finshield")

def migrate_csv_to_postgres():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    print("Creating tables if they don't exist...")
    # Enable pgvector extension
    with engine.connect() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    Base.metadata.create_all(engine)
    
    csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "transactions.csv")
    print(f"Reading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Load into transactions table
    print("Loading transactions into PostgreSQL...")
    # For a real migration, use to_sql with if_exists='append' or 'replace'
    df.to_sql('transactions', engine, if_exists='replace', index=False)
    
    print("Migration complete!")

if __name__ == "__main__":
    migrate_csv_to_postgres()
