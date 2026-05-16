import os
import httpx
import json

class Debater:
    def __init__(self, country, model_name="llama3:8b"):
        self.country = country
        self.model_name = os.getenv("LLM_MODEL_NAME", model_name)
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

    async def generate_response(self, topic, history):
        # Retrieve relevant policy points
        from core.rag_service import get_rag_service
        history_text = ""
        for msg in history:
            history_text += f"{msg['agent']}: {msg['message']} (Stance: {msg['stance']})\n"
        
        query = f"{topic} {history_text[-200:]}"
        relevant_points = get_rag_service().retrieve(query, self.country)
        policy_context = "\n".join([f"- {p}" for p in relevant_points])

        prompt = f"""Persona: Representative for {self.country}.
Topic: {topic}.
Policy: {policy_context}
History: {history_text[-500:]}

Instructions: Write one short paragraph stating your stance (supportive, opposed, or neutral) and reasoning. End with 'Stance: [stance]'.
"""

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": 150} # Shorten response
                    },
                    timeout=300.0
                )
                response.raise_for_status()
                result = response.json()
                content = result.get("response", "").strip()
                
                # Simple stance parsing
                stance = "neutral"
                if "supportive" in content.lower():
                    stance = "supportive"
                elif "opposed" in content.lower():
                    stance = "opposed"
                
                return content, stance
            except Exception as e:
                print(f"Error calling Ollama: {e}")
                return f"I apologize, but I am unable to provide a response at this time for {self.country}.", "neutral"
