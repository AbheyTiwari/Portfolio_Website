import os
import google.generativeai as genai
from typing import List, Dict

class GeminiProvider:
    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY missing")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model_name = model
    
    async def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """
        Generate response using Gemini API.
        messages = [{"role":"user"/"assistant"/"system","content":"..."}]
        Returns assistant text.
        """
        try:
            # Build conversation history for Gemini
            gemini_history = []
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    continue
                elif msg["role"] == "user":
                    user_messages.append(msg["content"])
                    gemini_history.append({
                        "role": "user",
                        "parts": [msg["content"]]
                    })
                elif msg["role"] == "assistant":
                    gemini_history.append({
                        "role": "model",
                        "parts": [msg["content"]]
                    })
            
            # Get the last user message
            if not user_messages:
                return "I didn't receive a message. Please try again."
            
            last_user_msg = user_messages[-1]
            
            # Create model instance
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            
            # Remove last message from history (will be sent separately)
            chat_history = gemini_history[:-1] if len(gemini_history) > 1 else []
            
            # Start chat with history
            chat = model.start_chat(history=chat_history)
            
            # Send the last message
            response = chat.send_message(last_user_msg)
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "Sorry, I encountered an error. Please try again in a moment."