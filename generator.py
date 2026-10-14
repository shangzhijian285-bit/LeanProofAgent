import os
import re

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

SYSTEM_PROMPT = (
    "You are a Lean 4 prover. "
    "Return only a proof beginning with `by`. "
    "Use only the provided imports. "
    "No Markdown, explanations, sorry, admit, or axioms."
)

IMPORTS = """
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
""".strip()


def generate_proof(theorem: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "deepseek-flash"),
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
Available imports:
{IMPORTS}

Theorem:
{theorem}
""".strip(),
            },
        ],
        extra_body={
            "thinking": {
                "type": "disabled"
            }
        },
    )

    proof = response.choices[0].message.content

    if not proof:
        raise ValueError("LLM returned an empty response.")

    proof = proof.strip()

    # 防止模型偶尔返回 ```lean ... ```
    if proof.startswith("```"):
        lines = proof.splitlines()

        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]

        proof = "\n".join(lines).strip()

    if not proof.startswith("by"):
        raise ValueError(
            f"LLM output is not a Lean tactic proof:\n{proof}"
        )

    if re.search(r"\b(sorry|admit|axiom)\b", proof):
        raise ValueError(
            f"Forbidden placeholder in generated proof:\n{proof}"
        )

    return proof


def repair_proof(
    theorem: str,
    failed_proof: str,
    error_message: str,
) -> str:
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "deepseek-flash"),
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
Available imports:
{IMPORTS}

Theorem:
{theorem}

Failed proof:
{failed_proof}

Lean error:
{error_message}

Fix the proof.
""".strip(),
            },
        ],
    )

    proof = response.choices[0].message.content

    if not proof:
        raise ValueError("LLM returned an empty response.")

    proof = proof.strip()

    if proof.startswith("```"):
        lines = proof.splitlines()
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        proof = "\n".join(lines).strip()

    return proof