
import ast
import difflib
import io
import os
import zipfile
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ReportLab PDF Generation Library
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

# Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.secrets.get("GEMINI_API_KEY", "")

client = genai.Client(api_key=api_key) if api_key else None

# Page Config
st.set_page_config(
    page_title="BugTrace AI | Code Audit Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# DEEP BLACK & RICH CHOCOLATE BROWN CSS THEME
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@500;700&display=swap');

    /* Global Deep Onyx & Warm Chocolate Theme */
    .stApp {
        background: #090807 !important;
        color: #F4EFEA !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Ambient Warm Chocolate & Bronze Floating Orbs */
    .stApp::before {
        content: "";
        position: fixed;
        top: -10%; left: -10%;
        width: 55vw; height: 55vw;
        background: radial-gradient(circle, rgba(140, 75, 28, 0.22) 0%, rgba(0,0,0,0) 70%);
        border-radius: 50%;
        animation: floatGlow 14s ease-in-out infinite alternate;
        pointer-events: none;
        z-index: 0;
    }

    .stApp::after {
        content: "";
        position: fixed;
        bottom: -10%; right: -10%;
        width: 50vw; height: 50vw;
        background: radial-gradient(circle, rgba(66, 36, 17, 0.28) 0%, rgba(0,0,0,0) 70%);
        border-radius: 50%;
        animation: floatGlow 16s ease-in-out infinite alternate-reverse;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes floatGlow {
        0% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(50px, 30px) scale(1.08); }
        100% { transform: translate(-20px, 60px) scale(0.95); }
    }

    /* Hero Banner Header */
    .hero-box {
        position: relative;
        background: rgba(24, 18, 14, 0.65);
        border: 1px solid rgba(217, 119, 6, 0.2);
        border-radius: 20px;
        padding: 32px;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin-bottom: 25px;
        overflow: hidden;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 40%, #B45309 70%, #78350F 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease infinite;
        letter-spacing: -1px;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .hero-subtitle {
        color: #C2A995;
        font-size: 1.05rem;
        margin-top: 6px;
    }

    /* Glass Panels */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(18, 14, 11, 0.55) !important;
        border: 1px solid rgba(217, 119, 6, 0.12) !important;
        border-radius: 18px !important;
        backdrop-filter: blur(16px) !important;
        transition: all 0.35s ease !important;
    }

    div[data-testid="stVerticalBlock"] > div:hover {
        border-color: rgba(217, 119, 6, 0.4) !important;
        box-shadow: 0 10px 30px rgba(180, 83, 9, 0.2) !important;
        transform: translateY(-2px);
    }

    /* Amber Pulsing Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        background: rgba(217, 119, 6, 0.12);
        color: #F59E0B;
        border: 1px solid rgba(217, 119, 6, 0.3);
        box-shadow: 0 0 15px rgba(217, 119, 6, 0.2);
    }

    .pulse-dot {
        width: 10px;
        height: 10px;
        background-color: #F59E0B;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 10px #F59E0B;
        animation: pulseAnimation 1.6s infinite;
    }

    @keyframes pulseAnimation {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.8); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
    }

    /* Chocolate & Amber Action Button */
    .stButton > button {
        background: linear-gradient(135deg, #78350F 0%, #B45309 50%, #D97706 100%) !important;
        background-size: 200% 200% !important;
        color: #FFFBEB !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px 32px !important;
        box-shadow: 0 8px 25px rgba(120, 53, 15, 0.5) !important;
        transition: all 0.35s ease !important;
    }

    .stButton > button:hover {
        background-position: 100% 0% !important;
        box-shadow: 0 12px 30px rgba(217, 119, 6, 0.6) !important;
        transform: translateY(-2px) scale(1.01) !important;
    }

    /* Input Fields */
    textarea, input[type="text"] {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: rgba(12, 9, 7, 0.85) !important;
        border: 1px solid rgba(217, 119, 6, 0.2) !important;
        color: #FBBF24 !important;
        border-radius: 12px !important;
    }
    textarea:focus, input[type="text"]:focus {
        border-color: #F59E0B !important;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.3) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 8, 6, 0.98) !important;
        border-right: 1px solid rgba(217, 119, 6, 0.12) !important;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        color: #A38A75 !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
    }
    button[aria-selected="true"] {
        background: rgba(217, 119, 6, 0.15) !important;
        color: #F59E0B !important;
        border: 1px solid rgba(217, 119, 6, 0.35) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# INTRO SPLASH ANIMATION LOGIC
# ---------------------------------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state["initialized"] = False

if not st.session_state["initialized"]:
    st.markdown(
        """
        <style>
        .splash-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 70vh;
            text-align: center;
        }

        .cyber-scanner-circle {
            position: relative;
            width: 130px;
            height: 130px;
            border-radius: 50%;
            border: 3px solid rgba(120, 53, 15, 0.3);
            border-top: 3px solid #F59E0B;
            border-bottom: 3px solid #78350F;
            animation: spin 2s linear infinite;
            margin-bottom: 30px;
            box-shadow: 0 0 25px rgba(245, 158, 11, 0.25);
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .splash-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #F59E0B 0%, #D97706 50%, #78350F 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
            margin-bottom: 10px;
        }

        .splash-text {
            color: #C2A995;
            font-size: 1.05rem;
            margin-bottom: 30px;
            font-family: 'JetBrains Mono', monospace;
        }
        </style>

        <div class="splash-wrapper">
            <div class="cyber-scanner-circle"></div>
            <div class="splash-title">BUGTRACE AI</div>
            <div class="splash-text">> Booting Neural Engines & Security Scanner...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("⚡ ENTER AUDIT TERMINAL", use_container_width=True):
            st.session_state["initialized"] = True
            st.rerun()

    st.stop()


# ---------------------------------------------------------------------------
# CORE BACKEND LOGIC
# ---------------------------------------------------------------------------
def check_python_syntax(code_str: str) -> tuple[bool, str]:
    try:
        ast.parse(code_str)
        return True, "⚡ AST ENGINE: Zero syntax faults detected."
    except SyntaxError as e:
        return False, f"❌ AST SYNTAX FAULT Line {e.lineno}: {e.msg}\n-> Code: {e.text}"


def fetch_github_file(github_url: str) -> str:
    raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    response = requests.get(raw_url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Unable to fetch repository stream. Status: {response.status_code}")


def extract_zip_files(uploaded_file) -> dict:
    allowed_extensions = {".py", ".js", ".java", ".cpp", ".c", ".h", ".cs", ".php", ".rb", ".go"}
    extracted_files = {}
    with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
        for file_info in zip_ref.infolist():
            if file_info.is_dir():
                continue
            if (
                file_info.filename.startswith("__MACOSX")
                or "node_modules" in file_info.filename
                or "venv" in file_info.filename
                or ".git" in file_info.filename
            ):
                continue
            ext = "." + file_info.filename.split(".")[-1] if "." in file_info.filename else ""
            if ext.lower() in allowed_extensions:
                try:
                    content = zip_ref.read(file_info.filename).decode("utf-8", errors="ignore")
                    if content.strip():
                        extracted_files[file_info.filename] = content
                except Exception:
                    pass
    return extracted_files


def analyze_code(source_code: str, language: str = "python", selected_checks: list = None) -> tuple[str, str]:
    if not client:
        raise ValueError("GEMINI_API_KEY environment variable missing!")

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

    system_prompt = f"""
    You are a friendly, encouraging, and easy-to-understand Code Mentor and Security Auditor.
    Explain issues in VERY SIMPLE, LAYMAN ENGLISH so that ANYONE can understand easily.

    Analyze the provided {language.upper()} code ONLY for the user-selected check categories listed below:
    SELECTED CHECKS TO PERFORM:
    {checks_str}

    STRICT INSTRUCTIONS FOR WRITING THE REPORT:
    1. Avoid overly dense technical jargon. Explain technical terms with real-life analogies.
    2. Explicitly explain the RISK LEVEL (High, Medium, Low) for every single issue.
    3. You MUST provide the fully fixed, clean version of the code inside a code block marked with `[FIXED_CODE_START]` and `[FIXED_CODE_END]`.

    FORMAT:
    ## 📢 Quick Code Health Summary
    - **Overall Status:** (Safe / Needs Minor Fixes / High Risk)
    - **Main Takeaway:** (1 simple sentence)

    ## 🚨 Issues Found & Simple Explanations
    (If no issues, state: "No major issues found in the selected categories!")

    For each issue:
    - ### Issue: [Name of Issue]
      - **Risk Level:** 
        - 🔴 **[HIGH RISK]:** Critical danger! (Explain impact)
        - 🟡 **[MEDIUM RISK]:** Warning! (Explain impact)
        - 🟢 **[LOW RISK]:** Minor issue. (Explain impact)
      - **Where in Code:** Line Number or Function Name
      - **What is Wrong (In Simple Words):** Clear explanation
      - **Real-Life Analogy:** Daily life example
      - **How to Fix:** Simple 1-sentence solution

    ## ⏱️ Code Speed & Efficiency (Easy Terms)
    - **Speed Rating:** (Super Fast / Slows down with large data)
    - **Simple Explanation:** Non-technical summary

    ## ✨ Fixed & Cleaned Code
    [FIXED_CODE_START]
    ```{language}
    # Clean, secure version of the code
    ```
    [FIXED_CODE_END]

    Source Code to Audit:
    ```{language}
    {source_code}
    ```
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=system_prompt,
    )
    report_text = response.text

    fixed_code = ""
    if "[FIXED_CODE_START]" in report_text and "[FIXED_CODE_END]" in report_text:
        try:
            raw_fixed = report_text.split("[FIXED_CODE_START]")[1].split("[FIXED_CODE_END]")[0]
            lines = raw_fixed.strip().split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            fixed_code = "\n".join(lines)
        except Exception:
            fixed_code = ""

    clean_report = report_text.replace("[FIXED_CODE_START]", "").replace("[FIXED_CODE_END]", "")
    return clean_report, fixed_code


def analyze_project_files(files_dict: dict, selected_checks: list = None) -> str:
    if not client:
        raise ValueError("GEMINI_API_KEY environment variable missing!")

    combined_code_block = ""
    for file_path, code in files_dict.items():
        combined_code_block += f"\n--- FILE: {file_path} ---\n{code}\n"

    system_prompt = f"""
    You are a Lead Software Security Auditor examining a MULTI-FILE PROJECT.
    Explain issues in VERY SIMPLE, LAYMAN ENGLISH.

    Analyze the following project codebase across files for cross-file vulnerabilities, security risks, bugs, and leaks.

    PROJECT CODEBASE:
    {combined_code_block}

    STRICT OUTPUT FORMAT:
    ## 📁 Project-Wide Executive Summary
    - **Total Files Scanned:** {len(files_dict)}
    - **Overall Project Risk:** 🔴 High Risk / 🟡 Moderate Risk / 🟢 Clean
    - **Critical Project Flaws:** (Summary of major cross-file or systemic issues)

    ## 🚨 File-by-File Detailed Vulnerability Breakdown
    (For EACH file containing issues, create a sub-section)

    ### 📄 File: [File Path]
    - **Risk Level:** (🔴 HIGH / 🟡 MEDIUM / 🟢 LOW)
    - **Issue Name:** Clear short title
    - **What is Wrong:** Simple explanation
    - **Real-Life Analogy:** Easy daily-life analogy
    - **How to Fix:** Simple fix recommendation

    ## 🛠️ Project Architectural Recommendations
    - **3 Key Steps to Secure this Project:** (Numbered list of top priorities)
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=system_prompt,
    )
    return response.text


def generate_pdf_report(report_text: str, filename: str = "Security_Audit_Report.pdf") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle", parent=styles["Heading1"], fontSize=20, textColor=colors.HexColor("#78350F"), spaceAfter=12
    )
    heading2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#18120E"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#3D312A"),
        spaceAfter=4,
    )

    story = [
        Paragraph("🛡️ BugTrace AI Security Audit Report", title_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#D97706"), spaceAfter=15),
    ]

    for line in report_text.split("\n"):
        line_str = line.strip()
        if not line_str:
            story.append(Spacer(1, 4))
            continue
        clean_line = (
            line_str.replace("**", "").replace("###", "").replace("##", "").replace("#", "").replace("`", "")
        )
        if line_str.startswith("##"):
            story.append(Paragraph(clean_line, heading2_style))
        elif line_str.startswith("-") or line_str.startswith("*"):
            story.append(Paragraph(f"• {clean_line[1:].strip()}", body_style))
        else:
            story.append(Paragraph(clean_line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_diff_html(original_code: str, fixed_code: str) -> str:
    diff = list(
        difflib.unified_diff(
            original_code.splitlines(),
            fixed_code.splitlines(),
            fromfile="Original Code",
            tofile="AI Secure Fixed Code",
            lineterm="",
        )
    )
    if not diff:
        return "<p style='color: #F59E0B;'>✅ Original code and fixed code are identical! No security patches required.</p>"

    html_lines = [
        "<div style='background-color: #0C0907; color: #E5D5C5; padding: 18px; border-radius: 14px; font-family:"
        " monospace; font-size: 13px; line-height: 1.6; border: 1px solid rgba(217, 119, 6, 0.25);'>"
    ]
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            html_lines.append(
                f"<div style='background-color: rgba(16, 185, 129, 0.18); color: #34d399; padding: 3px 8px;"
                f" border-radius: 6px; margin: 2px 0;'>{line}</div>"
            )
        elif line.startswith("-") and not line.startswith("---"):
            html_lines.append(
                f"<div style='background-color: rgba(244, 63, 94, 0.18); color: #fb7185; padding: 3px 8px;"
                f" border-radius: 6px; margin: 2px 0;'>{line}</div>"
            )
        elif line.startswith("@@"):
            html_lines.append(f"<div style='color: #F59E0B; font-weight: bold; margin: 10px 0;'>{line}</div>")
        else:
            html_lines.append(f"<div>{line}</div>")
    html_lines.append("</div>")
    return "\n".join(html_lines)


# ---------------------------------------------------------------------------
# MAIN APP DASHBOARD
# ---------------------------------------------------------------------------

# Hero Banner
st.markdown(
    """
    <div class="hero-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="hero-title">BUGTRACE AI</div>
                <div class="hero-subtitle">Automated Code Vulnerability & Performance Inspection Engine</div>
            </div>
            <div>
                <div class="status-badge">
                    <span class="pulse-dot"></span> AUDITOR ONLINE
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.markdown(
    "<h3 style='font-family: Space Grotesk; color: #F59E0B; letter-spacing: 1px;'>🛡️ AUDIT MATRIX</h3>",
    unsafe_allow_html=True,
)
check_cyber = st.sidebar.checkbox("🔒 Cyber Security (SQLi, Injection)", value=True)
check_memory = st.sidebar.checkbox("🧠 Memory & Resource Leaks", value=True)
check_concurrency = st.sidebar.checkbox("⚡ Race Conditions & Mutex Conflicts", value=True)
check_logic = st.sidebar.checkbox("🐞 Logical Flaws & Hidden Bugs", value=True)
check_performance = st.sidebar.checkbox("⏱️ Algorithmic Bottlenecks", value=True)
check_exceptions = st.sidebar.checkbox("🛡️ Crash Protection & Exception Logic", value=True)

selected_checks = []
if check_cyber:
    selected_checks.append("Cyber Security Risks")
if check_memory:
    selected_checks.append("Resource & Memory Leaks")
if check_concurrency:
    selected_checks.append("Race Conditions & Timing Conflicts")
if check_logic:
    selected_checks.append("Hidden Bugs & Logical Mistakes")
if check_performance:
    selected_checks.append("Performance & Speed Bottlenecks")
if check_exceptions:
    selected_checks.append("Crash Risks & Missing Exception Handling")

# Main Interface Columns
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown(
        "<h4 style='font-family: Space Grotesk; color: #F4EFEA;'>📥 SUBMISSION TERMINAL</h4>", unsafe_allow_html=True
    )

    tab_code, tab_github, tab_zip = st.tabs(["⚡ SINGLE FILE", "🔗 GITHUB REPO", "📦 ZIP ARCHIVE"])

    code_input = ""
    project_files = {}
    language = "python"
    input_mode = "Single"

    with tab_code:
        input_mode = "Single"
        language = st.selectbox("Target Language:", ["python", "javascript", "java", "cpp"])
        code_input = st.text_area("Source Code Buffer:", height=280, placeholder="Paste code snippet here...")

        if language == "python" and code_input.strip():
            if st.button("⚡ EXECUTE AST PRE-CHECK"):
                is_valid, msg = check_python_syntax(code_input)
                if is_valid:
                    st.success(msg)
                else:
                    st.error(msg)

    with tab_github:
        input_mode = "GitHub"
        language = st.selectbox("Repo Language:", ["python", "javascript", "java", "cpp"], key="gh_lang")
        github_url = st.text_input("GitHub Raw File URL:", placeholder="https://github.com/user/repo/blob/main/app.py")
        if github_url:
            with st.spinner("Streaming remote file content..."):
                try:
                    code_input = fetch_github_file(github_url)
                    st.success("✅ Remote stream linked successfully!")
                    st.text_area("Fetched Stream Preview:", code_input, height=180)
                except Exception as err:
                    st.error(f"Error: {str(err)}")

    with tab_zip:
        input_mode = "ZIP"
        uploaded_zip = st.file_uploader("Upload Full Project Archive (.ZIP)", type=["zip"])
        if uploaded_zip:
            project_files = extract_zip_files(uploaded_zip)
            if project_files:
                st.success(f"✅ Extracted {len(project_files)} code modules!")
                with st.expander("📁 Module Index"):
                    for fname in project_files.keys():
                        st.write(f"- `{fname}`")
            else:
                st.error("No valid code files found in archive.")

    analyze_button = st.button("🚀 INITIALIZE CYBER AUDIT SCAN", use_container_width=True)

with col_right:
    st.markdown(
        "<h4 style='font-family: Space Grotesk; color: #F4EFEA;'>📊 AUDIT INTELLIGENCE MATRIX</h4>",
        unsafe_allow_html=True,
    )

    if analyze_button:
        if input_mode == "ZIP":
            if not project_files:
                st.warning("⚠️ Please upload a valid ZIP archive.")
            else:
                with st.spinner("Analyzing multi-file codebase architecture..."):
                    try:
                        report_res = analyze_project_files(project_files, selected_checks)
                        st.session_state["report_res"] = report_res
                        st.session_state["fixed_code"] = ""
                        st.session_state["original_code"] = ""
                    except Exception as e:
                        st.error(f"Audit Error: {str(e)}")
        else:
            if not code_input.strip():
                st.warning("⚠️ Please provide source code prior to initializing scan.")
            else:
                with st.spinner("Executing neural threat evaluation & compiling audit..."):
                    try:
                        report_res, fixed_c = analyze_code(code_input, language, selected_checks)
                        st.session_state["report_res"] = report_res
                        st.session_state["fixed_code"] = fixed_c
                        st.session_state["original_code"] = code_input
                    except Exception as e:
                        st.error(f"Audit Error: {str(e)}")

    if "report_res" in st.session_state and st.session_state["report_res"]:
        st.markdown(st.session_state["report_res"])

        st.markdown("---")

        col_a, col_b = st.columns([1, 1])

        with col_a:
            try:
                pdf_bytes = generate_pdf_report(st.session_state["report_res"])
                st.download_button(
                    label="📥 EXPORT PDF AUDIT REPORT",
                    data=pdf_bytes,
                    file_name="BugTrace_Audit_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as pdf_err:
                st.error(f"PDF Error: {str(pdf_err)}")

        if st.session_state.get("fixed_code") and st.session_state.get("original_code"):
            with st.expander("🔀 SECURITY PATCH GIT DIFF VIEWER", expanded=True):
                diff_html = generate_diff_html(st.session_state["original_code"], st.session_state["fixed_code"])
                st.components.v1.html(diff_html, height=350, scrolling=True)
