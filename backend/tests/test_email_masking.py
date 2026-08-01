import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from helpers.email import mask_email

def test_mask_email():
    test_cases = [
        # (input_email, expected_output)
        ("user@example.com", "u**r@example.com"),
        ("ab@example.com", "a*@example.com"),
        ("a@example.com", "*@example.com"),
        ("john.doe@gmail.com", "j******e@gmail.com"),
        ("admin@church.org", "a***n@church.org"),
        ("", ""),
        (None, None),
        ("invalid_email", "invalid_email"),
    ]

    print("=== Testing email masking logic ===")
    print(f"{'Input Email':<30} | {'Masked Email':<30} | {'Status':<10}")
    print("-" * 76)

    failed = False
    for input_email, expected in test_cases:
        try:
            result = mask_email(input_email)
            status = "PASS" if result == expected else "FAIL"
            print(f"{str(input_email):<30} | {str(result):<30} | {status:<10}")
            if result != expected:
                print(f"  [ERROR] Expected: '{expected}', got: '{result}'")
                failed = True
        except Exception as e:
            print(f"{str(input_email):<30} | ERROR: {str(e):<23} | FAIL")
            failed = True

    if failed:
        print("\n[FAIL] Some test cases did not pass.")
        assert False, "Some test cases did not pass."
    else:
        print("\n[SUCCESS] All test cases passed successfully!")

if __name__ == "__main__":
    test_mask_email()
