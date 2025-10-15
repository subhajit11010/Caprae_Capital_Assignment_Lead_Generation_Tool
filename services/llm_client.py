from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
load_dotenv()

class LLMClient:
    def __init__(self):
        self.client = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key = os.getenv('GOOGLE_API_KEY'))
        # self.client.invoke()
        
    async def generate_text(self, prompt: str) -> str:
        response = await self.client.invoke([prompt]).generations[0][0].text
        return response