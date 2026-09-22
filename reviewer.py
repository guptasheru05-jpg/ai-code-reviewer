import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable missing in .env file"
    )

# Initialize Gemini Client
client = genai.Client(api_key=api_key)


def analyze_code(
    source_code: str, language: str = "python", selected_checks: list = None
) -> str:
    """Sends code to Gemini API and generates a simplified, layman-friendly security audit report."""

    if not selected_checks:
        selected_checks = [
            "Cyber Security Risks",
            "Resource & Memory Leaks",
            "Race Conditions & Timing Conflicts",
            "Hidden Bugs & Logical Mistakes",
            "Performance & Speed Bottlenecks",
            "Crash Risks & Missing Exception Handling",
        ]

    checks_str = "\n".join([f"- {check}" for check in selected_checks])

    # Simplified System Prompt with Risk Explanations and Layman Output
    system_prompt = f"""
    You are a friendly, encouraging, and easy-to-understand Code Mentor and Auditor.
    Your main goal is to explain code issues in VERY SIMPLE, LAYMAN ENGLISH so that ANYONE (even a non-technical manager or beginner student) can easily understand.

    Analyze the provided {language.upper()} code ONLY for the user-selected check categories listed below:

    SELECTED CHECKS TO PERFORM:
    {checks_str}

    STRICT INSTRUCTIONS FOR WRITING THE REPORT:
    1. Avoid overly dense technical jargon. If you use a technical term (like SQL Injection, Memory Leak, or Race Condition), EXPLAIN IT IMMEDIATELY in 1 simple sentence using a real-life analogy.
    2. Explicitly explain the RISK LEVEL (High, Medium, Low) for every single issue so the user knows WHY it matters.
    3. Output must strictly follow this exact Markdown structure:

    ##  Quick Code Health Summary
    - **Overall Status:** (e.g., Safe / Needs Minor Fixes / High Risk)
    - **Main Takeaway:** (1 simple sentence summarizing overall health)

    ##  Issues Found & Simple Explanations
    (If no issues are found for selected categories, state: "No major issues found in the selected categories!")

    For each issue matching the selected checks:
    - ### Issue: [Name of Issue]
      - **Risk Level:** 
        -  **[HIGH RISK]:** Critical danger! (Explain impact: e.g., Hackers can steal data or crash system immediately)
        -  **[MEDIUM RISK]:** Warning! (Explain impact: e.g., Can cause performance slowdowns or hidden bugs)
        -  **[LOW RISK]:** Minor issue. (Explain impact: e.g., Code works fine, but fixing makes it cleaner)
      - **Where in Code:** Line Number or Function Name
      - **What is Wrong (In Simple Words):** Explain problem clearly without complex coding jargon.
      - **Real-Life Analogy:** Simple daily-life example (e.g., "This is like leaving your main door unlocked.")
      - **How to Fix:** Simple 1-sentence solution.

    ##  Code Speed & Efficiency (Easy Terms)
    (Include ONLY if 'Performance & Speed Bottlenecks' is selected)
    - **Speed Rating:** (e.g., Super Fast / Slows down with large data)
    - **Simple Explanation:** Explain performance WITHOUT scary math notation (e.g., "If you give it 10 items, it takes 10 steps. If you give it 1,000 items, it takes 1,000 steps.")

    ##  Fixed & Cleaned Code
    ```{language}
    # Safe, refactored code with clear, simple comments
    ```

    ##  Automated Unit Tests (Verification)
    ```{language}
    # 2 simple test cases verifying the fix
    ```

    Source Code to Audit:
    ```{language}
    {source_code}
    ```
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=system_prompt,
    )

    return response.text