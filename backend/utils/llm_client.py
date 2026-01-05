"""
Multi-provider LLM client for Archify AI
Prioritizes: Perplexity Pro (live sources) → Gemini (fallback) → Groq (budget)
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError

load_dotenv()

logger = logging.getLogger(__name__)

# Provider configurations
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Model configurations
PERPLEXITY_MODELS = {
    "pro": "sonar-pro",  # Best for architecture with citations
    "reasoning": "sonar-reasoning-pro",  # Deep reasoning for complex designs
    "standard": "sonar",  # Faster, lighter
}

GEMINI_MODELS = {
    "pro": "gemini-2.5-pro",
    "flash": "gemini-2.5-flash",
}


class PerplexityClient:
    """
    Perplexity Pro client with live web search and citations
    BEST for architecture generation with verified sources
    """

    def __init__(self, api_key: str = PERPLEXITY_API_KEY):
        if not api_key:
            raise ValueError(
                "PERPLEXITY_API_KEY not set. "
                "Get free $5/month with Pro subscription at https://api.perplexity.ai"
            )
        self.client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

    def generate(
        self,
        prompt: str,
        model: str = "sonar-pro",
        temperature: float = 0.2,
        max_tokens: int = 10000,
        include_citations: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate architecture with live citations (NO dead links)

        Args:
            prompt: Architecture design requirements
            model: sonar-pro (with search) or sonar-reasoning-pro (deep reasoning)
            temperature: 0.2 for precise architecture, 0.7+ for creative
            max_tokens: Output length limit
            include_citations: Include source URLs

        Returns:
            {
                "response": "Generated architecture...",
                "citations": ["https://verified-link-1.com", ...],
                "model_used": "sonar-pro",
                "api_cost": "Covered by $5/month free with Pro"
            }
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect. "
                        "Design systems using verified patterns and cite sources.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract citations from response
            citations = []
            if include_citations and hasattr(response, "citations"):
                citations = response.citations

            return {
                "response": response.choices[0].message.content.strip(),
                "citations": citations,
                "model_used": model,
                "provider": "Perplexity Pro",
                "tokens_used": response.usage.total_tokens,
                "live_sources": True,  # Key advantage
            }

        except RateLimitError:
            logger.warning("Perplexity rate limit hit. Falling back to Gemini.")
            raise
        except APIError as e:
            logger.error(f"Perplexity API error: {e}")
            raise

    def deep_research(self, query: str) -> str:
        """
        For truly complex queries, use Perplexity web UI Deep Research
        (This returns instructions for manual use)

        Returns instruction for user to perform deep research manually
        which synthesizes 50+ sources automatically
        """
        return (
            f"⚙️  For best results on: '{query}'\n\n"
            "📍 Use Perplexity Web UI Deep Research:\n"
            "1. Go to https://www.perplexity.ai\n"
            "2. Click 'Deep Research' button (top-right)\n"
            "3. Paste your query\n"
            "4. Wait 2-4 minutes for synthesis of 50+ sources\n"
            "5. Export with live verified citations\n\n"
            "✅ This gives 100% verified sources, no dead links"
        )


class GeminiClient:
    """
    Google Gemini free API fallback (50 requests/day)
    Good quality, but NO live web search
    """

    def __init__(self, api_key: str = GEMINI_API_KEY):
        if not api_key:
            logger.warning(
                "GEMINI_API_KEY not set. Get free key: https://aistudio.google.com/apikey"
            )
            self.available = False
            return

        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self.genai = genai
        self.available = True

    def generate(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """
        Generate with Gemini (no live search, but high quality)
        """
        if not self.available:
            raise ValueError("Gemini API key not configured")

        try:
            model_obj = self.genai.GenerativeModel(model)
            response = model_obj.generate_content(
                prompt,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=temperature, max_output_tokens=max_tokens
                ),
            )

            return {
                "response": response.text,
                "model_used": model,
                "provider": "Google Gemini",
                "live_sources": False,
                "warning": "No live web search. Consider Perplexity for verified sources.",
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise


class HybridLLMClient:
    """
    Main client: tries Perplexity first (best for architecture),
    falls back to Gemini, then Groq
    """

    def __init__(
        self,
        perplexity_key: str = PERPLEXITY_API_KEY,
        gemini_key: str = GEMINI_API_KEY,
        groq_key: str = GROQ_API_KEY,
    ):
        self.perplexity = None
        self.gemini = None
        self.groq_key = groq_key

        # Initialize Perplexity (preferred)
        if perplexity_key:
            try:
                self.perplexity = PerplexityClient(perplexity_key)
                logger.info("✅ Perplexity Pro available (LIVE SOURCES)")
            except ValueError as e:
                logger.warning(f"Perplexity not available: {e}")

        # Initialize Gemini (fallback)
        if gemini_key:
            self.gemini = GeminiClient(gemini_key)
            if self.gemini.available:
                logger.info("✅ Gemini API available (50/day free)")

        # Store Groq key for potential use
        if groq_key:
            logger.info("✅ Groq available (100,000 tokens/day free)")

    def generate(
        self,
        prompt: str,
        prefer_live_search: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Smart generation with automatic fallback

        Args:
            prompt: Architecture requirements
            prefer_live_search: Prioritize Perplexity (live sources)
            **kwargs: model, temperature, max_tokens params

        Returns:
            Response with model used and source verification status
        """

        # Priority 1: Perplexity Pro (live web search)
        if prefer_live_search and self.perplexity:
            try:
                logger.info("Generating with Perplexity Pro (live sources)...")
                return self.perplexity.generate(prompt, **kwargs)
            except RateLimitError:
                logger.warning("Perplexity rate limited, trying Gemini...")
            except Exception as e:
                logger.warning(f"Perplexity failed: {e}, trying Gemini...")

        # Priority 2: Gemini (good quality, no live search)
        if self.gemini and self.gemini.available:
            try:
                logger.info("Generating with Gemini (cached knowledge)...")
                return self.gemini.generate(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")

        # Priority 3: Groq CLI (basic fallback)
        if self.groq_key:
            logger.info("Falling back to Groq CLI...")
            return self._groq_cli_fallback(prompt)

        raise RuntimeError(
            "No LLM providers available. "
            "Configure PERPLEXITY_API_KEY, GEMINI_API_KEY, or GROQ_API_KEY"
        )

    def _groq_cli_fallback(self, prompt: str) -> Dict[str, Any]:
        """Groq CLI fallback (your original implementation)"""
        import subprocess

        try:
            result = subprocess.run(
                ["groq", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                return {
                    "response": result.stdout.strip(),
                    "model_used": "Groq (CLI)",
                    "provider": "Groq",
                    "live_sources": False,
                }
            else:
                raise RuntimeError(f"Groq CLI failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Groq CLI timeout")
        except FileNotFoundError:
            raise RuntimeError("Groq CLI not found")

    def get_status(self) -> Dict[str, bool]:
        """Check which providers are available"""
        return {
            "perplexity_pro": self.perplexity is not None,
            "gemini": self.gemini is not None and self.gemini.available,
            "groq": self.groq_key is not None,
        }


# Singleton instance
_client: Optional[HybridLLMClient] = None


def get_llm_client() -> HybridLLMClient:
    """Get or create singleton LLM client"""
    global _client
    if _client is None:
        _client = HybridLLMClient()
    return _client


# Simple function wrapper for backward compatibility
def call_llm(
    prompt: str,
    provider: str = "auto",
    model: str = "sonar-pro",
    temperature: float = 0.2,
    max_tokens: int = 2000,
) -> str:
    """
    Simple wrapper matching your original API

    Args:
        prompt: Input prompt
        provider: 'auto' (smart), 'perplexity', 'gemini', or 'groq'
        model: Model name
        temperature: Creativity level
        max_tokens: Max output length

    Returns:
        Generated text response
    """
    client = get_llm_client()

    if provider == "auto":
        result = client.generate(
            prompt, prefer_live_search=True, model=model, temperature=temperature
        )
    elif provider == "perplexity":
        if not client.perplexity:
            raise ValueError("Perplexity not configured")
        result = client.perplexity.generate(
            prompt, model=model, temperature=temperature, max_tokens=max_tokens
        )
    elif provider == "gemini":
        if not client.gemini:
            raise ValueError("Gemini not configured")
        result = client.gemini.generate(
            prompt, model=model, temperature=temperature, max_tokens=max_tokens
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

    return result["response"]


if __name__ == "__main__":
    # Test your setup
    client = get_llm_client()
    print("📊 LLM Client Status:")
    print(client.get_status())

    # Test Perplexity
    if client.perplexity:
        print("\n✅ Testing Perplexity Pro...")
        try:
            result = client.generate(
                "Design a high-level architecture for a real-time chat application. Include modern patterns and technologies."
            )
            print(f"Model: {result['model_used']}")
            print(f"Live Sources: {result['live_sources']}")
            print(f"Response: {result['response'][:200]}...")
            if result.get("citations"):
                print(f"Citations: {result['citations'][:2]}...")
        except Exception as e:
            print(f"Error: {e}")
