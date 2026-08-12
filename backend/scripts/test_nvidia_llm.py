import os
from openai import OpenAI

api_key = os.getenv("NVIDIA_API_KEY", "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")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

print("=" * 60)
print("      TESTING NVIDIA NEMOTRON 550B ULTRA REASONING MODEL")
print("=" * 60)

prompt = "Explain how Retrieval-Augmented Generation (RAG) works in 3 clear sentences."

try:
    completion = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        top_p=0.95,
        max_tokens=1024,
        extra_body={"chat_template_kwargs": {"enable_thinking": True}, "reasoning_budget": 1024},
        stream=True
    )

    print("\n--- REASONING & OUTPUT STREAM ---")
    reasoning_text = ""
    content_text = ""

    for chunk in completion:
        if not chunk.choices:
            continue
        reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
        if reasoning:
            reasoning_text += reasoning
            print(f"[Thinking] {reasoning}", end="", flush=True)
        if chunk.choices[0].delta.content is not None:
            content_text += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end="", flush=True)

    print("\n\n" + "=" * 60)
    print("      NVIDIA NEMOTRON 550B ULTRA TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR testing NVIDIA Nemotron: {e}")
