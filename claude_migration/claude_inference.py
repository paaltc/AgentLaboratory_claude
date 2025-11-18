"""
Claude Code Migration - Inference Module
Replaces multi-model inference.py with Claude-focused implementation
"""
import os
import time
import json
import anthropic
from typing import Optional, List, Dict, Any

# Token tracking for cost estimation
TOKENS_IN = {}
TOKENS_OUT = {}

# Claude pricing (as of 2025)
CLAUDE_PRICING = {
    "claude-sonnet-4-5-20250929": {
        "input": 3.00 / 1_000_000,
        "output": 15.00 / 1_000_000,
    },
    "claude-3-5-sonnet-latest": {
        "input": 3.00 / 1_000_000,
        "output": 15.00 / 1_000_000,
    },
    "claude-3-opus-20240229": {
        "input": 15.00 / 1_000_000,
        "output": 75.00 / 1_000_000,
    },
    "claude-3-haiku-20240307": {
        "input": 0.25 / 1_000_000,
        "output": 1.25 / 1_000_000,
    },
}


def get_current_cost() -> float:
    """Calculate current total cost from token usage."""
    total = 0.0
    for model, tokens in TOKENS_IN.items():
        if model in CLAUDE_PRICING:
            total += CLAUDE_PRICING[model]["input"] * tokens
    for model, tokens in TOKENS_OUT.items():
        if model in CLAUDE_PRICING:
            total += CLAUDE_PRICING[model]["output"] * tokens
    return total


def get_token_stats() -> Dict[str, Dict[str, int]]:
    """Get detailed token usage statistics."""
    stats = {}
    for model in set(list(TOKENS_IN.keys()) + list(TOKENS_OUT.keys())):
        stats[model] = {
            "input_tokens": TOKENS_IN.get(model, 0),
            "output_tokens": TOKENS_OUT.get(model, 0),
            "total_tokens": TOKENS_IN.get(model, 0) + TOKENS_OUT.get(model, 0),
        }
    return stats


class ClaudeClient:
    """Wrapper for Anthropic Claude API with cost tracking and retry logic."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude client with API key."""
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or provided")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = "claude-sonnet-4-5-20250929"

    def query(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 8192,
        tools: Optional[List[Dict[str, Any]]] = None,
        retries: int = 5,
        retry_delay: float = 5.0,
        print_cost: bool = True,
    ) -> str:
        """
        Query Claude model with retry logic and cost tracking.

        Args:
            prompt: User message content
            system_prompt: System instructions
            model: Claude model to use (default: claude-sonnet-4-5-20250929)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            tools: List of tool definitions for tool use
            retries: Number of retry attempts
            retry_delay: Delay between retries in seconds
            print_cost: Whether to print cost estimate

        Returns:
            Model response text
        """
        model = model or self.default_model

        for attempt in range(retries):
            try:
                # Build message request
                kwargs = {
                    "model": model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                }

                if system_prompt:
                    kwargs["system"] = system_prompt

                if temperature is not None:
                    kwargs["temperature"] = temperature

                if tools:
                    kwargs["tools"] = tools

                # Make API call
                response = self.client.messages.create(**kwargs)

                # Extract response text
                response_json = json.loads(response.to_json())

                # Handle different response types
                content = response_json.get("content", [])
                text_parts = []
                tool_uses = []

                for block in content:
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif block.get("type") == "tool_use":
                        tool_uses.append(block)

                answer = "\n".join(text_parts)

                # If there were tool uses, append them to the response
                if tool_uses:
                    answer += f"\n\n[TOOL_CALLS: {json.dumps(tool_uses)}]"

                # Track token usage
                usage = response_json.get("usage", {})
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)

                if model not in TOKENS_IN:
                    TOKENS_IN[model] = 0
                    TOKENS_OUT[model] = 0

                TOKENS_IN[model] += input_tokens
                TOKENS_OUT[model] += output_tokens

                if print_cost:
                    cost = get_current_cost()
                    print(f"Current experiment cost = ${cost:.6f} (Claude API)")

                return answer

            except anthropic.RateLimitError as e:
                print(f"Rate limit hit (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            except anthropic.APIError as e:
                print(f"API error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(retry_delay)
                continue
            except Exception as e:
                print(f"Unexpected error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(retry_delay)
                continue

        raise Exception(f"Max retries ({retries}) exceeded")

    def query_with_tools(
        self,
        prompt: str,
        system_prompt: str,
        tools: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: Optional[float] = None,
        print_cost: bool = True,
    ) -> Dict[str, Any]:
        """
        Query Claude with tool definitions and handle tool use responses.

        Args:
            prompt: User message content
            system_prompt: System instructions
            tools: List of tool definitions
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            print_cost: Whether to print cost estimate

        Returns:
            Dictionary containing:
                - text: Text response from model
                - tool_calls: List of tool use blocks (if any)
                - stop_reason: Why the model stopped
        """
        model = model or self.default_model

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        if temperature is not None:
            kwargs["temperature"] = temperature

        response = self.client.messages.create(**kwargs)
        response_json = json.loads(response.to_json())

        # Parse response
        content = response_json.get("content", [])
        text_parts = []
        tool_calls = []

        for block in content:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                tool_calls.append({
                    "id": block.get("id"),
                    "name": block.get("name"),
                    "input": block.get("input"),
                })

        # Track token usage
        usage = response_json.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        if model not in TOKENS_IN:
            TOKENS_IN[model] = 0
            TOKENS_OUT[model] = 0

        TOKENS_IN[model] += input_tokens
        TOKENS_OUT[model] += output_tokens

        if print_cost:
            cost = get_current_cost()
            print(f"Current experiment cost = ${cost:.6f} (Claude API)")

        return {
            "text": "\n".join(text_parts),
            "tool_calls": tool_calls,
            "stop_reason": response_json.get("stop_reason", ""),
            "usage": usage,
        }

    def conversation(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 8192,
        tools: Optional[List[Dict[str, Any]]] = None,
        print_cost: bool = True,
    ) -> Dict[str, Any]:
        """
        Handle multi-turn conversations with Claude.

        Args:
            messages: List of conversation messages
            system_prompt: System instructions
            model: Claude model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            tools: Optional tool definitions
            print_cost: Whether to print cost estimate

        Returns:
            Dictionary containing response details
        """
        model = model or self.default_model

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        if temperature is not None:
            kwargs["temperature"] = temperature

        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)
        response_json = json.loads(response.to_json())

        # Track token usage
        usage = response_json.get("usage", {})
        if model not in TOKENS_IN:
            TOKENS_IN[model] = 0
            TOKENS_OUT[model] = 0

        TOKENS_IN[model] += usage.get("input_tokens", 0)
        TOKENS_OUT[model] += usage.get("output_tokens", 0)

        if print_cost:
            cost = get_current_cost()
            print(f"Current experiment cost = ${cost:.6f} (Claude API)")

        return response_json


def query_claude(
    prompt: str,
    system_prompt: str = "",
    model: str = "claude-sonnet-4-5-20250929",
    temperature: Optional[float] = None,
    max_tokens: int = 8192,
    api_key: Optional[str] = None,
    retries: int = 5,
    retry_delay: float = 5.0,
    print_cost: bool = True,
) -> str:
    """
    Convenience function for querying Claude (similar to original query_model).

    Args:
        prompt: User message content
        system_prompt: System instructions
        model: Claude model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        api_key: Anthropic API key (optional, uses env var)
        retries: Number of retry attempts
        retry_delay: Delay between retries
        print_cost: Whether to print cost estimate

    Returns:
        Model response text
    """
    client = ClaudeClient(api_key=api_key)
    return client.query(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        retries=retries,
        retry_delay=retry_delay,
        print_cost=print_cost,
    )


# Compatibility wrapper for existing code
def query_model(
    model_str: str,
    prompt: str,
    system_prompt: str,
    openai_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    tries: int = 5,
    timeout: float = 5.0,
    temp: Optional[float] = None,
    print_cost: bool = True,
    version: str = "1.5",
) -> str:
    """
    Backwards-compatible wrapper that routes all calls to Claude.

    Maps old model names to Claude models:
    - gpt-4o, gpt-4o-mini, o1, o3-mini, deepseek-chat -> claude-sonnet-4-5
    - claude-3.5-sonnet -> claude-sonnet-4-5
    """
    # Map old model names to Claude
    model_mapping = {
        "gpt-4o": "claude-sonnet-4-5-20250929",
        "gpt4o": "claude-sonnet-4-5-20250929",
        "gpt-4o-mini": "claude-sonnet-4-5-20250929",
        "gpt4omini": "claude-sonnet-4-5-20250929",
        "gpt-4omini": "claude-sonnet-4-5-20250929",
        "gpt4o-mini": "claude-sonnet-4-5-20250929",
        "o1": "claude-sonnet-4-5-20250929",
        "o1-mini": "claude-sonnet-4-5-20250929",
        "o1-preview": "claude-sonnet-4-5-20250929",
        "o3-mini": "claude-sonnet-4-5-20250929",
        "deepseek-chat": "claude-sonnet-4-5-20250929",
        "claude-3.5-sonnet": "claude-sonnet-4-5-20250929",
        "claude-3-5-sonnet": "claude-sonnet-4-5-20250929",
        "gemini-2.0-pro": "claude-sonnet-4-5-20250929",
        "gemini-1.5-pro": "claude-sonnet-4-5-20250929",
    }

    claude_model = model_mapping.get(model_str, "claude-sonnet-4-5-20250929")

    # Use provided API key or fall back to environment variable
    api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

    return query_claude(
        prompt=prompt,
        system_prompt=system_prompt,
        model=claude_model,
        temperature=temp,
        api_key=api_key,
        retries=tries,
        retry_delay=timeout,
        print_cost=print_cost,
    )


if __name__ == "__main__":
    # Test the client
    print("Testing Claude inference module...")

    # Check if API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set. Set it to test the module.")
        print("Example usage:")
        print('  export ANTHROPIC_API_KEY="your-key-here"')
        print('  python claude_inference.py')
    else:
        # Simple test
        response = query_claude(
            prompt="What is 2 + 2?",
            system_prompt="You are a helpful assistant. Be concise.",
            print_cost=True,
        )
        print(f"Response: {response}")
        print(f"\nToken stats: {get_token_stats()}")
        print(f"Total cost: ${get_current_cost():.6f}")
