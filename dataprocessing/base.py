import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



"""
Command to start database instance:
docker run --name sqlalchemy-orm-psql \
    -e POSTGRES_PASSWORD=DB_USER \
    -e POSTGRES_USER=DB_PASSWORD \
    -e POSTGRES_DB=sqlalchemy \
    -p 5432:5432 \
    -d postgres
"""

USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')

engine = create_engine(f'postgresql://{USER}:{PASSWORD}@localhost:5432/sqlalchemy')
Session = sessionmaker(bind=engine)

Base = declarative_base()
