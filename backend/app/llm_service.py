import asyncio
from typing import List, Optional
from .config import settings

class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        """Initialize LLM service"""
        self.mock_mode = True  # Set to False when using real LLM
        self.model_name = settings.LLM_MODEL_NAME
        
        # For production with Ollama:
        # import ollama
        # self.client = ollama.Client()
        # self.mock_mode = False
        
        print(f"LLM Service initialized (mock_mode={self.mock_mode})")
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[List[str]] = None,
        conversation_history: Optional[List] = None
    ) -> str:
        """
        Generate response using LLM
        
        Args:
            prompt: User query
            context: Retrieved knowledge context
            conversation_history: Previous messages
            
        Returns:
            Generated response
        """
        if self.mock_mode:
            return await self._mock_generate(prompt, context)
        else:
            return await self._real_generate(prompt, context, conversation_history)
    
    async def _mock_generate(self, prompt: str, context: Optional[List[str]]) -> str:
        """Mock LLM responses for development"""
        # Simulate API delay
        await asyncio.sleep(1.0)
        
        prompt_lower = prompt.lower()
        
        # Contextual responses
        if context and len(context) > 0:
            context_snippet = context[0][:150]
            return (
                f"Based on the information in my knowledge base: '{context_snippet}...', "
                f"I can help you with that. {prompt} "
                f"I found {len(context)} relevant source(s) to answer your question. "
                f"Would you like me to elaborate on any specific aspect?"
            )
        
        # Identity questions
        if any(word in prompt_lower for word in ["who are you", "what are you", "introduce yourself"]):
            return (
                "I'm JARVIS, your personal AI assistant! I'm powered by a self-hosted large language model "
                "and use a vector database for intelligent knowledge retrieval. I can help you store, "
                "organize, and retrieve information through natural conversation. Think of me as your "
                "second brain - add knowledge to my database, and I'll help you recall and connect "
                "information whenever you need it!"
            )
        
        # Capability questions
        if any(word in prompt_lower for word in ["what can you do", "capabilities", "features", "help"]):
            return (
                "I can help you with several things:\n\n"
                "1. 💬 Answer questions using RAG (Retrieval-Augmented Generation)\n"
                "2. 📚 Store and retrieve knowledge from a vector database\n"
                "3. 🔍 Find relevant information based on semantic similarity\n"
                "4. 📄 Process and understand uploaded documents\n"
                "5. 💡 Provide context-aware responses using your personal knowledge base\n\n"
                "To get started, try adding some knowledge through the Knowledge tab, "
                "then ask me questions about it!"
            )
        
        # How/why questions
        if prompt_lower.startswith(("how ", "why ", "what ", "when ", "where ")):
            return (
                f"That's a great question about '{prompt}'. To provide you with the most accurate answer, "
                f"I recommend adding relevant information to my knowledge base through the Knowledge tab. "
                f"Once you do that, I'll be able to give you detailed, context-aware responses using "
                f"retrieval-augmented generation. Would you like to know more about how my RAG system works?"
            )
        
        # Default response
        return (
            f"I understand you're asking about: '{prompt}'. "
            f"While I can engage in general conversation, I work best when you've added relevant "
            f"information to my knowledge base. This allows me to provide accurate, context-specific answers "
            f"using retrieval-augmented generation. Try adding some documents or text in the Knowledge tab!"
        )
    
    async def _real_generate(
        self,
        prompt: str,
        context: Optional[List[str]],
        conversation_history: Optional[List]
    ) -> str:
        """Generate response using real LLM (Ollama)"""
        # Build system prompt with context
        system_prompt = (
            "You are JARVIS, a helpful and intelligent AI assistant. "
            "You provide accurate, thoughtful responses based on the context provided."
        )
        
        if context and len(context) > 0:
            system_prompt += "\n\nRelevant context from knowledge base:\n"
            for i, ctx in enumerate(context, 1):
                system_prompt += f"{i}. {ctx}\n"
            system_prompt += "\nUse this context to answer the question accurately."
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Call Ollama
        # import ollama
        # response = self.client.chat(
        #     model=self.model_name,
        #     messages=messages,
        #     stream=False
        # )
        # return response['message']['content']
        
        # Placeholder for now
        return "Real LLM integration - Ollama not configured yet"

# Global instance
llm_service = LLMService()