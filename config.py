import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')