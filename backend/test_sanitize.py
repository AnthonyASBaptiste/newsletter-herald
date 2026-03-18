from helpers.text_utils import sanitize_filename
import logging

# Set up logging to see warnings
logging.basicConfig(level=logging.INFO)

test_files = [
    "2nd Sunday of Advent - 8Dec2024_20241207_064550_0000.pdf",
    "_HTP Newsletter Sunday 15 Feb 2026 (1).pdf",
    "05.10.25.pdf",
    "1 Sept 2019 Newsletter.pdf",
    "29Sept2024-compressed.pdf",
    "NEWSLETTER Sunday 15th March 2025_20250315_162554_0000.pdf",
    "Holy Trinity Newsletter_01.12.24-3.pdf",
    "Holy Trinity Newsletter 6th April 2025.pdf",
    "FEAST of EPIPHANY - Sunday 5th January 2025.pdf",
    "Feb 1 2026 Newsletter.pdf",
    "NoDateFile.pdf"
]

print(f"{'Original Filename':<60} | {'Sanitized Filename':<40}")
print("-" * 105)
for f in test_files:
    sanitized = sanitize_filename(f)
    print(f"{f:<60} | {sanitized:<40}")
