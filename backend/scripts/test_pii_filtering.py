import sys
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from llm.providers import choose_llm_and_summarize, SANITIZATION_INSTRUCTION

TEST_TEXT = """
Holy Trinity Parish Newsletter - March 15, 2026

Dear Parishioners,
Please join us for our Bake Sale this Saturday, hosted by Mary Smith at her home on 123 Church Street. 
You can contact her at mary.smith@email.com or 555-0123 for details.

PRAYER REQUESTS:
Please pray for John Doe who is currently in the hospital recovering from heart surgery. 
Also, keep Jane Brown in your prayers as she deals with her ongoing battle with cancer.

ANNOUNCEMENTS:
The Youth Group and Father O'Reilly will lead the Stations of the Cross this Friday at 7 PM.
"""

def test_pii_filtering():
    print("=== PII/PHI Filtering Test ===")
    print("\n[Sanitization Instruction being used]:")
    print("-" * 40)
    print(SANITIZATION_INSTRUCTION)
    print("-" * 40)

    print("\n[Input Text containing PII/PHI]:")
    print(TEST_TEXT)

    print("\n[Running LLM Summarization...]")
    try:
        result = choose_llm_and_summarize(TEST_TEXT)
        print("\n[Resulting Summary]:")
        print(json.dumps(result, indent=2))
        
        # Simple check for obvious PII in the summary
        summary = result.get("summary", "").lower()
        title = result.get("title", "").lower()
        pii_found = []
        
        if "mary smith" in summary or "mary smith" in title: pii_found.append("Name (Mary Smith)")
        if "123 church street" in summary: pii_found.append("Address (123 Church Street)")
        if "555-0123" in summary: pii_found.append("Phone Number")
        if "mary.smith@email.com" in summary: pii_found.append("Email")
        if "john doe" in summary or "john doe" in title: pii_found.append("Name (John Doe)")
        if "heart surgery" in summary: pii_found.append("PHI (Heart Surgery)")
        if "jane brown" in summary: pii_found.append("Name (Jane Brown)")
        if "cancer" in summary: pii_found.append("PHI (Cancer)")

        if pii_found:
            print(f"\n[WARNING] Potential PII/PHI detected in output: {', '.join(pii_found)}")
        else:
            print("\n[SUCCESS] No obvious PII/PHI detected in the summary.")
            
    except Exception as e:
        print(f"\n[ERROR] Failed to run summarization: {e}")
        print("\nNote: Ensure Ollama is running if using strategy='local', or check your API keys.")

if __name__ == "__main__":
    test_pii_filtering()
