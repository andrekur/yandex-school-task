from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import dotenv_values

CONFIG = dotenv_values('_CI/.env')

USER = CONFIG['DB_USER']
PASSWORD = CONFIG['DB_PASSWORD']
HOST = CONFIG['DB_HOST']
PORT = int(CONFIG['DB_PORT'])
DB = CONFIG['DB_NAME_DB']

engine = create_engine(
    f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}')

Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()
