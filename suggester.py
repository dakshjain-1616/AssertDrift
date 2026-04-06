"""OpenRouter integration for assertion improvement suggestions."""

import ast
import os
import time
from typing import List, Dict
from openai import OpenAI

OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
MODEL = "qwen/qwen3.6-plus:free"


def get_api_key() -> str:
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")
    return api_key


def generate_suggestion(test_name: str, assertion_source: str, score: float) -> str:
    """Ask the model to rewrite a weak assertion into a stronger one."""
    api_key = get_api_key()
    client = OpenAI(api_key=api_key, base_url=OPENROUTER_API_URL)

    prompt = (
        f"Test function: {test_name}\n"
        f"Current assertion (score {score:.1f}/3 — weak):\n"
        f"    {assertion_source}\n\n"
        "Rewrite this as a stronger assertion that checks an exact value, "
        "specific state, or concrete output. Return only the replacement line, "
        "no explanation."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a senior software engineer improving test quality."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=120,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(suggestion unavailable: {e})"


def _assertion_source(test_func: Dict) -> str:
    """Build a readable string of the assertions in a test function."""
    lines = []
    for a in test_func['assertions']:
        lines.append(f"line {a['lineno']}: score={a['score']}")
    return "; ".join(lines) if lines else "(no assertions)"


def generate_suggestions_for_results(results: List[Dict]) -> List[str]:
    """Return one suggestion string per test function, in iteration order.

    Tests with avg score >= 1.5 get an empty string (no suggestion needed).
    """
    suggestions = []
    for result in results:
        for test_func in result['test_functions']:
            assertions = test_func['assertions']
            if assertions:
                avg = sum(a['score'] for a in assertions) / len(assertions)
            else:
                avg = 0.0

            if avg < 1.5:
                hint = generate_suggestion(
                    test_name=test_func['name'],
                    assertion_source=_assertion_source(test_func),
                    score=avg,
                )
                suggestions.append(hint)
                time.sleep(1.5)  # avoid free-tier rate limit
            else:
                suggestions.append("")
    return suggestions
