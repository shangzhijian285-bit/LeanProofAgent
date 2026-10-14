import re
import subprocess
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


DEFAULT_IMPORTS = """
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
"""


def build_lean_code(
    theorem: str,
    proof: str,
    imports: str = DEFAULT_IMPORTS,
) -> str:
    """
    把 theorem 和 proof 拼成完整、可交给 Lean 检查的代码。
    """
    return f"""
{imports.strip()}

{theorem.strip()} := {proof.strip()}
"""


def parse_lean_errors(output: str):
    pattern = re.compile(
        r"^(.*?\.lean):(\d+):(\d+): error: (.*)$",
        re.MULTILINE,
    )

    matches = list(pattern.finditer(output))
    errors = []

    for i, match in enumerate(matches):
        file_name = match.group(1)
        line = int(match.group(2))
        column = int(match.group(3))

        message_start = match.start(4)

        if i + 1 < len(matches):
            message_end = matches[i + 1].start()
        else:
            message_end = len(output)

        message = output[message_start:message_end].strip()

        errors.append(
            {
                "file": file_name,
                "line": line,
                "column": column,
                "message": message,
            }
        )

    return errors


def verify_lean(code: str, timeout: int = 60):
    lean_file = PROJECT_ROOT / "_Verify.lean"
    lean_file.write_text(code, encoding="utf-8")

    try:
        result = subprocess.run(
            ["lean", str(lean_file)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )

        full_output = result.stdout + "\n" + result.stderr

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "errors": parse_lean_errors(full_output),
            "raw_output": full_output.strip(),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": None,
            "errors": [],
            "raw_output": "",
            "system_error": f"Lean verification timed out after {timeout} seconds.",
        }

    finally:
        lean_file.unlink(missing_ok=True)


if __name__ == "__main__":
    theorem = """
example (x : ℝ) :
    (x + 1)^2 = x^2 + 2*x + 1
"""

    proof = """
by
  ring
"""

    code = build_lean_code(theorem, proof)

    print("Generated Lean code:")
    print("--------------------")
    print(code)
    print("--------------------")

    start = time.perf_counter()

    result = verify_lean(code)

    elapsed = time.perf_counter() - start

    print(result)
    print("time:", elapsed)