# llm.py
from langchain_google_genai import ChatGoogleGenerativeAI
import os

from dotenv import  load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
