"""
Modulo: claude_service.py
Descrizione: Servizio per interazione con Claude API (Anthropic)
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import anthropic
from anthropic import AsyncAnthropic
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Servizio per chiamate Claude API.

    Features:
    - Chat completions
    - Streaming support
    - Context management
    - Token counting
    """

    def __init__(self):
        """Initialize Claude client"""
        self.api_key = settings.CLAUDE_API_KEY
        if not self.api_key:
            logger.warning("CLAUDE_API_KEY not configured - AI chatbot will not work")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=self.api_key)
            logger.info("Claude API client initialized")

    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        model: str = "claude-sonnet-4-5-20250929",
    ) -> Dict[str, Any]:
        """
        Create chat completion with Claude API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling (0-1)
            model: Claude model to use

        Returns:
            Dict with 'content', 'id', 'stop_reason', 'usage'

        Raises:
            Exception: If API call fails
        """
        if not self.client:
            raise Exception("Claude API client not initialized - check CLAUDE_API_KEY")

        try:
            # Prepare request
            request_params = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
            }

            if system_prompt:
                request_params["system"] = system_prompt

            logger.debug(f"Calling Claude API with {len(messages)} messages")

            # Call API
            response = await self.client.messages.create(**request_params)

            # Extract response
            result = {
                "content": response.content[0].text if response.content else "",
                "id": response.id,
                "stop_reason": response.stop_reason,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            }

            logger.info(
                f"Claude API call successful - "
                f"Input: {result['usage']['input_tokens']} tokens, "
                f"Output: {result['usage']['output_tokens']} tokens"
            )

            return result

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise

    async def create_chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        model: str = "claude-sonnet-4-5-20250929",
    ) -> AsyncGenerator[str, None]:
        """
        Create streaming chat completion with Claude API.

        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
            model: Claude model to use

        Yields:
            Text chunks as they arrive

        Raises:
            Exception: If API call fails
        """
        if not self.client:
            raise Exception("Claude API client not initialized - check CLAUDE_API_KEY")

        try:
            request_params = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
            }

            if system_prompt:
                request_params["system"] = system_prompt

            logger.debug(f"Starting streaming Claude API call with {len(messages)} messages")

            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield text

            # Get final message after stream completes
            final_message = await stream.get_final_message()

            logger.info(
                f"Claude streaming completed - "
                f"Input: {final_message.usage.input_tokens} tokens, "
                f"Output: {final_message.usage.output_tokens} tokens"
            )

        except anthropic.APIError as e:
            logger.error(f"Claude API streaming error: {e}")
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Claude streaming: {e}")
            raise

    def count_tokens(self, text: str, model: str = "claude-sonnet-4-5-20250929") -> int:
        """
        Estimate token count for text.

        Note: Uses rough approximation (1 token ≈ 4 chars).
        For exact counts, use Claude API's count_tokens endpoint.

        Args:
            text: Text to count
            model: Model to use for counting

        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        # More accurate: use Anthropic's tokenizer when available
        return len(text) // 4

    def build_rag_system_prompt(
        self,
        context_chunks: List[str],
        base_instructions: str = None,
    ) -> str:
        """
        Build system prompt with RAG context.

        Args:
            context_chunks: Retrieved text chunks from knowledge base
            base_instructions: Base instructions for the AI

        Returns:
            Complete system prompt with context
        """
        if not base_instructions:
            base_instructions = (
                "Sei un assistente esperto in AI, GDPR, Cybersecurity e NIS2. "
                "Rispondi in italiano in modo professionale e accurato. "
                "Usa le informazioni fornite nel contesto per rispondere alle domande."
            )

        if not context_chunks:
            return base_instructions

        # Build context section
        context_text = "\n\n---\n\n".join(context_chunks)

        prompt = f"""{base_instructions}

# CONTESTO INFORMATIVO

Le seguenti informazioni sono state recuperate dalla nostra knowledge base e potrebbero essere rilevanti per rispondere alla domanda dell'utente:

{context_text}

---

Usa queste informazioni per rispondere, ma non citarle esplicitamente. Rispondi in modo naturale come se conoscessi già questi dettagli. Se le informazioni fornite non sono sufficienti per rispondere alla domanda, dillo chiaramente."""

        return prompt

    def validate_message_content(self, content: str) -> bool:
        """
        Validate message content before sending to API.

        Args:
            content: Message content to validate

        Returns:
            True if valid, False otherwise
        """
        if not content or not content.strip():
            return False

        # Check length (Claude limit is ~200k tokens)
        token_count = self.count_tokens(content)
        if token_count > 180000:  # Leave margin
            logger.warning(f"Message too long: {token_count} tokens")
            return False

        return True


# Singleton instance
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """Get singleton Claude service instance"""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service


logger.debug("Claude service module loaded")
