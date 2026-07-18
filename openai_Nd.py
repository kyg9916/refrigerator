from openai import OpenAI
import os
import sys

_USE_COLOR = sys.stdout.isatty() and os.getenv("NO_COLOR") is None
_REASONING_COLOR = "\033[90m" if _USE_COLOR else ""
_RESET_COLOR = "\033[0m" if _USE_COLOR else ""

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

completion = client.chat.completions.create(
    model="z-ai/glm-5.2",
    messages=[{"role": "user", "content": "방울토마토를 냉장보관하면 얼마나 보관할 수 있어?"}],
    temperature=0.5,
    top_p=1,
    max_tokens=2048,
    seed=42,

    stream=True
)

for chunk in completion:
    if not getattr(chunk, "choices", None):
        continue
    if len(chunk.choices) == 0 or getattr(chunk.choices[0], "delta", None) is None:
        continue
    delta = chunk.choices[0].delta
    if getattr(delta, "content", None) is not None:
        print(delta.content, end="")