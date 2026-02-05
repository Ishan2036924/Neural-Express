"""OpenAI LLM client wrapper."""

import json
from typing import Optional
from openai import OpenAI, OpenAIError

from ..utils.logging import get_logger

logger = get_logger("summarize.llm")


class LLMClient:
    """Wrapper for OpenAI API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize LLM client.

        Args:
            api_key: OpenAI API key
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(f"Initialized OpenAI client with model {model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate completion from prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            json_mode: If True, enforce JSON response format

        Returns:
            Generated text

        Raises:
            OpenAIError: If API call fails
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response_format = {"type": "json_object"} if json_mode else {"type": "text"}

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=response_format
            )

            content = response.choices[0].message.content

            logger.debug(
                f"Generated {len(content)} chars "
                f"(tokens: {response.usage.total_tokens})"
            )

            return content

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> dict:
        """
        Generate JSON response from prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON dict

        Raises:
            OpenAIError: If API call fails
            json.JSONDecodeError: If response is not valid JSON
        """
        response = self.generate(
            prompt,
            system_prompt=system_prompt,
            json_mode=True
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response content: {response}")
            raise
