from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# .env file se API key load karne ke liye
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

class ChatRequest(BaseModel):
    storeUrl: str  # Ab yahan manual catalog ki jagah website ka link aayega
    customerMessage: str

@app.post("/api/chat-widget")
async def chat_with_store_bot(req: ChatRequest):
    try:
        # 1. Diye gaye website URL se automatically data fetch aur scrape karna
        headers = {'User-Agent': 'Mozilla/5.0'}
        web_response = requests.get(req.storeUrl, headers=headers, timeout=10)
        soup = BeautifulSoup(web_response.text, 'html.parser')
        
        # Faltu script aur style tags ko hata dena taaki clean text mile
        for script in soup(["script", "style"]):
            script.extract()
            
        store_content = soup.get_text(separator=' ', strip=True)[:4000] # Token overflow se bachne ke liye text limit

        # 2. Gemini AI ko website ke scraped content ke sath prompt bhejna
        prompt = f"""
        You are an expert, polite shopping assistant for the website: {req.storeUrl}.
        Here is the scraped content/catalog of the website:
        {store_content}
        
        Answer the customer's query based ONLY on this website data. If information is not found, politely guide them.
        Customer Query: {req.customerMessage}
        """
        
        response = model.generate_content(prompt)
        return {"reply": response.text}
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))