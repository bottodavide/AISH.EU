"""
Modulo: guardrails_service.py
Descrizione: Servizio guardrails per sicurezza e controllo AI chatbot
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
import re
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.chat import AIGuardrailConfig

logger = logging.getLogger(__name__)


class GuardrailsService:
    """
    Servizio per guardrails AI chatbot.

    Features:
    - Input validation and filtering
    - Output validation and filtering
    - Topic enforcement
    - Rate limiting
    - Content moderation
    - Blacklist/whitelist management
    """

    def __init__(self):
        """Initialize guardrails service"""
        # In-memory rate limiting (in production, use Redis)
        self._rate_limit_cache: Dict[str, List[datetime]] = {}

        # Default blocked patterns
        self._blocked_patterns = [
            r"<script[^>]*>.*?</script>",  # XSS
            r"<iframe[^>]*>.*?</iframe>",  # iframe injection
            r"javascript:",  # javascript: protocol
            r"on\w+\s*=",  # event handlers
        ]

        # Default allowed topics
        self._allowed_topics = {
            "AI",
            "GDPR",
            "NIS2",
            "CYBERSECURITY",
            "GENERAL",
        }

        logger.info("Guardrails service initialized")

    async def load_config(self, db: AsyncSession) -> Optional[AIGuardrailConfig]:
        """
        Load guardrails configuration from database.

        Args:
            db: Database session

        Returns:
            Configuration or None
        """
        try:
            query = select(AIGuardrailConfig).where(AIGuardrailConfig.is_active == True)
            result = await db.execute(query)
            config = result.scalar_one_or_none()

            if config:
                logger.debug("Guardrails config loaded from database")
            else:
                logger.warning("No active guardrails config found")

            return config

        except Exception as e:
            logger.error(f"Error loading guardrails config: {e}")
            return None

    def validate_input(
        self,
        user_input: str,
        config: Optional[AIGuardrailConfig] = None,
    ) -> Dict[str, Any]:
        """
        Validate user input before sending to AI.

        Args:
            user_input: User message
            config: Optional guardrails configuration

        Returns:
            Dict with 'valid', 'reason', 'filtered_input'
        """
        try:
            # Check length
            if len(user_input) < 1:
                return {
                    "valid": False,
                    "reason": "Input is empty",
                    "filtered_input": user_input,
                }

            if len(user_input) > 5000:
                return {
                    "valid": False,
                    "reason": "Input exceeds maximum length (5000 characters)",
                    "filtered_input": user_input,
                }

            # Check for blocked patterns (XSS, injection)
            for pattern in self._blocked_patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    logger.warning(f"Blocked input with pattern: {pattern}")
                    return {
                        "valid": False,
                        "reason": "Input contains prohibited content",
                        "filtered_input": user_input,
                    }

            # Apply config-based filtering
            if config:
                # Check blacklist
                if config.blacklist_topics:
                    for blocked_topic in config.blacklist_topics:
                        if blocked_topic.lower() in user_input.lower():
                            logger.warning(f"Blocked input with blacklisted topic: {blocked_topic}")
                            return {
                                "valid": False,
                                "reason": f"Topic '{blocked_topic}' is not allowed",
                                "filtered_input": user_input,
                            }

                # Check whitelist (if enforced)
                if config.whitelist_topics and config.enforce_topic_whitelist:
                    topic_found = False
                    for allowed_topic in config.whitelist_topics:
                        if allowed_topic.lower() in user_input.lower():
                            topic_found = True
                            break

                    if not topic_found:
                        logger.warning("Input does not match whitelist topics")
                        return {
                            "valid": False,
                            "reason": "Query topic not allowed",
                            "filtered_input": user_input,
                        }

                # Filter profanity (if enabled)
                if config.filter_profanity:
                    filtered = self._filter_profanity(user_input)
                    if filtered != user_input:
                        logger.info("Profanity filtered from input")
                        user_input = filtered

            return {
                "valid": True,
                "reason": None,
                "filtered_input": user_input,
            }

        except Exception as e:
            logger.error(f"Error validating input: {e}")
            return {
                "valid": False,
                "reason": "Input validation error",
                "filtered_input": user_input,
            }

    def validate_output(
        self,
        ai_output: str,
        config: Optional[AIGuardrailConfig] = None,
    ) -> Dict[str, Any]:
        """
        Validate AI output before returning to user.

        Args:
            ai_output: AI response
            config: Optional guardrails configuration

        Returns:
            Dict with 'valid', 'reason', 'filtered_output'
        """
        try:
            # Check length
            if len(ai_output) < 1:
                return {
                    "valid": False,
                    "reason": "Output is empty",
                    "filtered_output": ai_output,
                }

            # Check for blocked patterns
            for pattern in self._blocked_patterns:
                if re.search(pattern, ai_output, re.IGNORECASE):
                    logger.warning(f"Blocked output with pattern: {pattern}")
                    # Remove the pattern instead of blocking
                    ai_output = re.sub(pattern, "", ai_output, flags=re.IGNORECASE)

            # Apply config-based filtering
            if config:
                # Filter profanity
                if config.filter_profanity:
                    filtered = self._filter_profanity(ai_output)
                    if filtered != ai_output:
                        logger.info("Profanity filtered from output")
                        ai_output = filtered

            return {
                "valid": True,
                "reason": None,
                "filtered_output": ai_output,
            }

        except Exception as e:
            logger.error(f"Error validating output: {e}")
            return {
                "valid": False,
                "reason": "Output validation error",
                "filtered_output": ai_output,
            }

    def check_rate_limit(
        self,
        identifier: str,
        config: Optional[AIGuardrailConfig] = None,
    ) -> Dict[str, Any]:
        """
        Check rate limiting for user/session.

        Args:
            identifier: User ID or session ID
            config: Optional guardrails configuration

        Returns:
            Dict with 'allowed', 'reason', 'retry_after'
        """
        try:
            # Get rate limit settings
            max_requests = config.max_requests_per_hour if config else 50
            time_window = timedelta(hours=1)

            # Get or create request history
            if identifier not in self._rate_limit_cache:
                self._rate_limit_cache[identifier] = []

            request_history = self._rate_limit_cache[identifier]

            # Clean old requests
            cutoff_time = datetime.utcnow() - time_window
            request_history[:] = [ts for ts in request_history if ts > cutoff_time]

            # Check limit
            if len(request_history) >= max_requests:
                oldest_request = min(request_history)
                retry_after = int((oldest_request + time_window - datetime.utcnow()).total_seconds())

                logger.warning(f"Rate limit exceeded for {identifier}")

                return {
                    "allowed": False,
                    "reason": f"Rate limit exceeded. Max {max_requests} requests per hour.",
                    "retry_after": max(retry_after, 0),
                }

            # Add current request
            request_history.append(datetime.utcnow())

            return {
                "allowed": True,
                "reason": None,
                "retry_after": None,
            }

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Allow request on error (fail open)
            return {
                "allowed": True,
                "reason": None,
                "retry_after": None,
            }

    def validate_topic(
        self,
        topic: str,
        config: Optional[AIGuardrailConfig] = None,
    ) -> Dict[str, Any]:
        """
        Validate topic against whitelist/blacklist.

        Args:
            topic: Topic to validate
            config: Optional guardrails configuration

        Returns:
            Dict with 'valid', 'reason'
        """
        try:
            topic_upper = topic.upper()

            # Check blacklist
            if config and config.blacklist_topics:
                if topic_upper in [t.upper() for t in config.blacklist_topics]:
                    return {
                        "valid": False,
                        "reason": f"Topic '{topic}' is blacklisted",
                    }

            # Check whitelist (if enforced)
            if config and config.whitelist_topics and config.enforce_topic_whitelist:
                if topic_upper not in [t.upper() for t in config.whitelist_topics]:
                    return {
                        "valid": False,
                        "reason": f"Topic '{topic}' is not in whitelist",
                    }

            # Check against default allowed topics
            if topic_upper not in self._allowed_topics:
                return {
                    "valid": False,
                    "reason": f"Topic '{topic}' is not recognized",
                }

            return {
                "valid": True,
                "reason": None,
            }

        except Exception as e:
            logger.error(f"Error validating topic: {e}")
            return {
                "valid": False,
                "reason": "Topic validation error",
            }

    def _filter_profanity(self, text: str) -> str:
        """
        Filter profanity from text.

        Simple implementation - replace with proper profanity filter library.

        Args:
            text: Text to filter

        Returns:
            Filtered text
        """
        # Basic profanity list (extend as needed)
        profanity_list = [
            "fuck",
            "shit",
            "damn",
            "ass",
            "bitch",
            # Add more as needed
        ]

        filtered_text = text
        for word in profanity_list:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            filtered_text = pattern.sub("*" * len(word), filtered_text)

        return filtered_text

    def get_system_instructions(
        self,
        config: Optional[AIGuardrailConfig] = None,
    ) -> str:
        """
        Get system instructions for AI based on guardrails.

        Args:
            config: Optional guardrails configuration

        Returns:
            System instructions text
        """
        instructions = []

        # Base instructions
        instructions.append(
            "Sei un assistente professionale e rispettoso. "
            "Rispondi solo a domande relative ai topic autorizzati."
        )

        # Topic restrictions
        if config:
            if config.whitelist_topics:
                topics_str = ", ".join(config.whitelist_topics)
                instructions.append(
                    f"Rispondi SOLO a domande su questi argomenti: {topics_str}. "
                    "Per altri argomenti, declina educatamente."
                )

            if config.blacklist_topics:
                topics_str = ", ".join(config.blacklist_topics)
                instructions.append(
                    f"NON rispondere MAI a domande su questi argomenti: {topics_str}."
                )

            # Custom instructions
            if config.custom_instructions:
                instructions.append(config.custom_instructions)

        return " ".join(instructions)

    def clear_rate_limit_cache(self):
        """Clear rate limit cache (for testing)"""
        self._rate_limit_cache.clear()
        logger.info("Rate limit cache cleared")


# Singleton instance
_guardrails_service: Optional[GuardrailsService] = None


def get_guardrails_service() -> GuardrailsService:
    """Get singleton guardrails service instance"""
    global _guardrails_service
    if _guardrails_service is None:
        _guardrails_service = GuardrailsService()
    return _guardrails_service


logger.debug("Guardrails service module loaded")
