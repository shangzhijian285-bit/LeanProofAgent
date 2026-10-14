from generator import generate_proof, repair_proof
from verifier import build_lean_code, verify_lean


def main():
    theorem = """
example (x : ℝ)
    (h : x^4 - 10*x^2 + 9 = 0) :
    x = 1 ∨ x = -1 ∨ x = 3 ∨ x = -3
"""

    proof = generate_proof(theorem)

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        print(f"\n=== Attempt {attempt} ===")
        print(proof)

        code = build_lean_code(theorem, proof)
        result = verify_lean(code)

        if result["success"]:
            print("\n✓ Proof verified!")
            return

        print("\n✗ Proof failed.")

        error_message = "\n\n".join(
            error["message"]
            for error in result["errors"]
        )

        print(error_message)

        if attempt == max_attempts:
            break

        proof = repair_proof(
            theorem=theorem,
            failed_proof=proof,
            error_message=error_message,
        )

    print("\nFailed after maximum attempts.")


if __name__ == "__main__":
    main()