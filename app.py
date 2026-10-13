import streamlit as st
import streamlit.components.v1 as components
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import html
import json

st.set_page_config(page_title="Faculty Question Collection Portal", page_icon="📘", layout="wide")

# Faculty allocation supplied by the user
FACULTY = {
    "P MOHAN": {
        "emp_id": "54788", "module": "Module – 1",
        "topics": "Functions of two variables; partial derivatives; total differential; Jacobian and its properties; Taylor’s expansion for two variables",
        "difficulty": ["Easy", "Medium", "Medium"],
    },
    "DEVI YAMINI S": {
        "emp_id": "51016", "module": "Module – 1",
        "topics": "Maxima and minima; constrained maxima and minima; Lagrange’s multiplier method",
        "difficulty": ["Medium", "Easy", "Hard"],
    },
    "SAGITHYA T": {
        "emp_id": "53117", "module": "Module – 2",
        "topics": "Evaluation of double integrals; change of order of integration; change of variables between Cartesian and polar coordinates",
        "difficulty": ["Easy", "Easy", "Medium"],
    },
    "SAURABH CHANDRA MAURY": {
        "emp_id": "52253", "module": "Module – 2",
        "topics": "Evaluation of triple integrals; change of variables between Cartesian, cylindrical, and spherical coordinates",
        "difficulty": ["Hard", "Hard", "Easy"],
    },
    "OM NAMHA SHIVAY": {
        "emp_id": "52271", "module": "Module – 3",
        "topics": "Scalar and vector-valued functions; gradient; directional derivative; divergence; curl; scalar and vector potentials",
        "difficulty": ["Medium", "Easy", "Easy"],
    },
    "FATHIMA SAFIKAA S N": {
        "emp_id": "54965", "module": "Module – 3",
        "topics": "Line, surface, and volume integrals; statements of Green’s, Stokes’, and Gauss’s divergence theorems",
        "difficulty": ["Medium", "Medium", "Medium"],
    },
    "ARNAB KAYAL": {
        "emp_id": "54766", "module": "Module – 3",
        "topics": "Verification and evaluation of vector integrals using Green’s, Stokes’, and Gauss’s theorems",
        "difficulty": ["Hard", "Hard", "Hard"],
    },
    "ABHISHEK KUMAR SINGH": {
        "emp_id": "50611", "module": "Module – 4",
        "topics": "Linear second-order ordinary differential equations with constant coefficients; method of undetermined coefficients; variation of parameters",
        "difficulty": ["Medium", "Medium", "Easy"],
    },
    "KOMAL KUMAR": {
        "emp_id": "54779", "module": "Module – 4",
        "topics": "Solutions of Cauchy–Euler and Cauchy–Legendre differential equations",
        "difficulty": ["Medium", "Medium", "Medium"],
    },
    "LAKSHMANAN S": {
        "emp_id": "52269", "module": "Module – 4",
        "topics": "Applications of linear second-order differential equations",
        "difficulty": ["Easy", "Hard", "Hard"],
    },
    "SRUTHA KEERTHI B": {
        "emp_id": "50431", "module": "Module – 5",
        "topics": "Formation of PDE; first-order PDEs of the forms F(p,q)=0, F(z,p,q)=0, F(x,p)=G(y,q), and Clairaut’s form",
        "difficulty": ["Hard", "Medium", "Medium"],
    },
    "SOUMENDU ROY": {
        "emp_id": "52803", "module": "Module – 5",
        "topics": "Lagrange’s equation Pp + Qq = R; solution of a linear first-order PDE by separation of variables",
        "difficulty": ["Easy", "Easy", "Easy"],
    },
}
BT_LEVELS = [
    "BT1 - Remember", "BT2 - Understand", "BT3 - Apply",
    "BT4 - Analyze", "BT5 - Evaluate", "BT6 - Create"
]

def get_worksheet():
    """Connect using Streamlit secrets. Supports service-account JSON stored as a dict."""
    if "gcp_service_account" not in st.secrets:
        raise RuntimeError("Google Sheets credentials are not configured in Streamlit secrets.")
    info = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(
        info,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    client = gspread.authorize(creds)
    spreadsheet_id = st.secrets.get("google_sheet_id")
    if not spreadsheet_id:
        raise RuntimeError("Add google_sheet_id to Streamlit secrets.")
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet_name = st.secrets.get("worksheet_name", "Question Submissions")
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=12)
    headers = [
        "Submitted At", "Employee ID", "Faculty Name", "Module", "Assigned Topics",
        "Question Number", "Difficulty", "BT Level", "Question LaTeX", "Rubrics", "Status"
    ]
    if not worksheet.get_all_values():
        worksheet.append_row(headers)
    return worksheet

def render_latex_preview(source, key):
    # MathJax renders inline $...$ and display $$...$$ notation.
    safe_source = html.escape(source).replace("\n", "<br>")
    template = """<!doctype html><html><head>
    <meta charset="utf-8">
    <script>
    window.MathJax = {tex: {inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$','$$'], ['\\\\[','\\\\]']]}, svg: {fontCache: 'global'}};
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
    <style>
      body {font-family: Arial, sans-serif; color: #202124; margin: 0; padding: 12px;}
      .question {font-size: 16px; line-height: 1.65; overflow-wrap: anywhere;}
    </style></head><body><div class="question">__QUESTION__</div></body></html>"""
    page = template.replace("__QUESTION__", safe_source or "<em>Your rendered question will appear here.</em>")
    components.html(page, height=180, scrolling=True)

st.title("📘 BAMAT101 - Multivariable Calculus and Differential Equations - FAT Question Paper Submission Form")
st.write("Select your name to view your assigned module, topics, and difficulty levels. Enter three questions with Bloom’s Taxonomy level and rubrics, preview the question, then submit.")

with st.sidebar:
    st.header("Faculty details")
    faculty_name = st.selectbox("Select your name", ["— Select faculty —"] + sorted(FACULTY.keys()))
    if faculty_name != "— Select faculty —":
        faculty = FACULTY[faculty_name]
        st.text_input("Employee ID", value=faculty["emp_id"], disabled=True)
        st.text_input("Assigned module", value=faculty["module"], disabled=True)
    st.caption("Only the selected faculty member’s assigned questions are shown.")

if faculty_name == "— Select faculty —":
    st.info("Please select your name from the Faculty details panel to begin.")
    st.stop()

faculty = FACULTY[faculty_name]
st.subheader(f"{faculty['module']} · {faculty_name}")
st.markdown("**Assigned topics**")
st.write(faculty["topics"])
st.divider()

with st.form("question_submission_form"):
    entries = []
    for i in range(3):
        st.markdown(f"### Question {i + 1}")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.text_input("Assigned difficulty", value=faculty["difficulty"][i], disabled=True, key=f"diff_{i}")
        with c2:
            bt = st.selectbox("Bloom’s Taxonomy level", BT_LEVELS, key=f"bt_{i}")
        q = st.text_area(
            "Question (enter LaTeX where needed)",
            key=f"question_{i}",
            height=130,
            placeholder=r"Example: Find $\frac{\partial z}{\partial x}$ for $z=x^2y+xy^2$.",
            help=r"Use $...$ for inline mathematics and $$...$$ or \[...\] for display mathematics."
        )
        rubric = st.text_area(
            "Rubrics (include expected steps and marks)",
            key=f"rubric_{i}",
            height=100,
            placeholder="Example: Correct method (2 marks); working (2 marks); final answer (1 mark)."
        )
        with st.expander(f"Preview Question {i + 1}", expanded=False):
            render_latex_preview(q, f"preview_{i}")
            st.caption("Preview uses MathJax. Confirm the rendered equations before submitting.")
        entries.append({"number": i + 1, "difficulty": faculty["difficulty"][i], "bt": bt, "question": q, "rubrics": rubric})
        if i < 2:
            st.divider()

    submitted = st.form_submit_button("Submit all 3 questions", type="primary", use_container_width=True)

if submitted:
    missing = []
    for entry in entries:
        if not entry["question"].strip():
            missing.append(f"Question {entry['number']}")
        if not entry["rubrics"].strip():
            missing.append(f"Rubrics for Question {entry['number']}")
    if missing:
        st.error("Please complete all required fields: " + ", ".join(missing) + ".")
    else:
        try:
            worksheet = get_worksheet()
            submitted_at = datetime.now().astimezone().isoformat(timespec="seconds")
            rows = []
            for entry in entries:
                rows.append([
                    submitted_at, faculty["emp_id"], faculty_name, faculty["module"],
                    faculty["topics"], entry["number"], entry["difficulty"], entry["bt"],
                    entry["question"].strip(), entry["rubrics"].strip(), "Submitted"
                ])
            worksheet.append_rows(rows, value_input_option="USER_ENTERED")
            st.success("Your three questions have been submitted successfully.")
            st.info("You may close this page after confirming submission.")
        except Exception as exc:
            st.error("Submission could not be saved to Google Sheets. Please check the app configuration or contact the coordinator.")
            st.code(str(exc))
