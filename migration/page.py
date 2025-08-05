from sqlalchemy import create_engine, Column, Integer, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Define the base and model

Base = declarative_base()


class Page(Base):
    __tablename__ = "pages_fix"

    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    content = Column(Text, nullable=True)
    status = Column(Integer, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    embedding = Column(JSON, nullable=True)  # ✅ Corrected
    title = Column(Text, nullable=True)  # ✅ Corrected
    token = Column(Integer, default=0)


# PostgreSQL connection URL
DB_URL = "postgresql://mukhtada:password@localhost:5432/chatbot"

# Set up engine and session
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# Create table
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("✅ Table created in PostgreSQL")
