from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env file se variables load karega
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ab yeh secure tarike se .env file se key uthayega
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

class ChatRequest(BaseModel):
    storeId: str
    customerMessage: str
    productCatalog: str

@app.post("/api/chat-widget")
async def chat_with_store_bot(req: ChatRequest):
    try:
        prompt = f"""
        You are a smart, polite shopping assistant for an e-commerce store (Store ID: {req.storeId}).
        Here is the product catalog and store details:
        {req.productCatalog}
        
        Answer the customer's query based ONLY on this catalog. If a product isn't available, suggest a similar alternative.
        Customer Query: {req.customerMessage}
        """
        
        response = model.generate_content(prompt)
        return {"reply": response.text}
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))