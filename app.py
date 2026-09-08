import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 1. Page Configuration
st.set_page_config(
    page_title="CareerPulse AI - Resume & Career Advisor", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS Styling (Executive Dark Slate & Royal Blue Theme)
st.markdown("""
    <style>
        /* Base page theme */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0b1329;
            border-right: 1px solid #1e293b;
        }
        
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #38bdf8 !important;
        }

        /* Headings & Text */
        h1, h2, h3, h4 {
            color: #f8fafc !important;
            font-weight: 700;
        }
        
        .main-header {
            background: linear-gradient(90deg, #2563eb 0%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }
        
        .sub-header {
            color: #94a3b8;
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }

        /* Cards & Container Containers */
        .portal-card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            max-width: 550px;
            margin: 2rem auto;
        }

        /* Chat Messages */
        [data-testid="stChatMessage"] {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            padding: 1.2rem !important;
            margin-bottom: 1rem !important;
            color: #f1f5f9 !important;
        }

        /* Chat Input Styling */
        [data-testid="stChatInput"] {
            background-color: #1e293b !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 12px !important;
        }
        
        [data-testid="stChatInput"] textarea {
            color: #f8fafc !important;
        }

        [data-testid="stChatInput"] button {
            background-color: #2563eb !important;
            color: white !important;
            border-radius: 8px !important;
        }

        /* Streamlit Buttons */
        div.stButton > button {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
            width: 100%;
        }
        
        div.stButton > button:hover {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
            transform: translateY(-1px);
        }

        /* Feature pills */
        .feature-pill {
            background-color: #0f172a;
            border: 1px solid #334155;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #38bdf8;
            display: inline-block;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Define Career Specialist System Prompt
CAREER_PULSE_SYSTEM_PROMPT = (
    "You are CareerPulse AI, an elite executive tech recruiter, ATS (Applicant Tracking System) specialist, "
    "and senior career advisor with 15+ years of experience helping candidates land top-tier roles.\n\n"
    "When a user provides a resume, job description, cover letter, or career bullet points, analyze them thoroughly "
    "and output a structured, high-impact report using markdown headers and clear bullet points containing:\n\n"
    "🎯 **ATS & Impact Score**: Provide an overall evaluation score (out of 10) with a 2-sentence executive summary.\n"
    "💪 **Core Strengths**: List top 3 standout qualifications, hard/soft skills, or key achievements.\n"
    "⚠️ **Critical Gaps & Missing Keywords**: Identify key industry terms, action verbs, or formatting improvements needed.\n"
    "🚀 **High-Impact Bullet Point Rewrites**: Take 2-3 weak bullet points and rewrite them using the formula: "
    "[Strong Action Verb] + [Specific Task/Context] + [Quantifiable Metric/Result].\n"
    "💡 **Next Strategic Steps**: Provide 2 immediate actionable tips to boost interview landing rates.\n\n"
    "Keep the tone encouraging, professional, sharp, and results-oriented."
)

# 4. Session State Initialization
if "api_authenticated" not in st.session_state:
    st.session_state["api_authenticated"] = False
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = "gpt-5-nano"
if "temperature" not in st.session_state:
    st.session_state["temperature"] = 0.3
if "pending_prompt" not in st.session_state:
    st.session_state["pending_prompt"] = None

# Ensure System Message is registered in session history
def reset_system_message():
    st.session_state["messages"] = [SystemMessage(content=CAREER_PULSE_SYSTEM_PROMPT)]

if not st.session_state["messages"] or not isinstance(st.session_state["messages"][0], SystemMessage):
    reset_system_message()

# 5. Lock Screen / Access Portal
if not st.session_state["api_authenticated"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #38bdf8;'>💼 CareerPulse AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>Unlock your personalized AI Career Coach & ATS Resume Auditor.</p>", unsafe_allow_html=True)
        
        with st.form("api_key_form"):
            st.markdown("### Access Portal")
            api_key_input = st.text_input("OpenAI API Key", type="password", placeholder="sk-proj-...")
            submit_button = st.form_submit_button("Unlock Dashboard 🚀")
            
            if submit_button:
                if api_key_input.strip() != "":
                    st.session_state["api_key"] = api_key_input.strip()
                    st.session_state["api_authenticated"] = True
                    st.rerun()
                else:
                    st.error("Please enter a valid OpenAI API key to proceed.")

        st.markdown("""
            <div style='margin-top: 1.5rem; text-align: center;'>
                <span class='feature-pill'>🎯 ATS Scoring</span>
                <span class='feature-pill'>📝 Resume Rewrites</span>
                <span class='feature-pill'>⚡ Keyword Optimization</span>
                <span class='feature-pill'>📧 Cover Letter Review</span>
            </div>
            <p style='text-align: center; font-size: 0.8rem; color: #64748b; margin-top: 1rem;'>
                🔒 Your API key is stored strictly in temporary session memory and is never logged or saved.
            </p>
        """, unsafe_allow_html=True)
    st.stop()

# 6. Sidebar Controls & Presets
with st.sidebar:
    st.markdown("## 💼 CareerPulse AI")
    st.caption("AI Resume Auditor & Career Strategist")
    st.divider()

    st.markdown("### ⚙️ Model Settings")
    model_options = ["gpt-5-nano", "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    current_model = st.session_state.get("selected_model", "gpt-5-nano")
    default_idx = model_options.index(current_model) if current_model in model_options else 0
    st.session_state["selected_model"] = st.selectbox(
        "OpenAI Model",
        model_options,
        index=default_idx
    )
    
    st.session_state["temperature"] = st.slider(
        "Analysis Tone / Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Lower values produce strict analytical scoring; higher values offer creative rewrites."
    )
    
    st.divider()
    st.markdown("### ⚡ Quick Presets")
    
    if st.button("📄 Full Resume & ATS Audit"):
        st.session_state["pending_prompt"] = (
            "Please conduct a full ATS audit on my resume below. Score it out of 10, point out missing tech skills/keywords, "
            "and suggest strong metrics to add:\n\n[PASTE YOUR RESUME HERE]"
        )
        st.rerun()
        
    if st.button("🎯 Match Resume to Job Description"):
        st.session_state["pending_prompt"] = (
            "Compare my resume against this Target Job Description. Highlight gaps, matching keywords, and how to tailor my bullet points:\n\n"
            "**TARGET JOB DESCRIPTION:**\n[PASTE JOB DESCRIPTION HERE]\n\n"
            "**MY RESUME:**\n[PASTE YOUR RESUME HERE]"
        )
        st.rerun()

    if st.button("⚡ Bullet Point Enhancer"):
        st.session_state["pending_prompt"] = (
            "Rewrite the following resume bullet points using powerful action verbs and quantifiable results/metrics:\n\n"
            "- Worked on website design and improved load times.\n"
            "- Managed a team of 4 junior developers.\n"
            "- Responsible for resolving user tickets and fixing software bugs."
        )
        st.rerun()

    if st.button("📧 Cover Letter Review"):
        st.session_state["pending_prompt"] = (
            "Review my cover letter below for impact, tone, and engagement. Provide constructive edits and a polished version:\n\n[PASTE COVER LETTER HERE]"
        )
        st.rerun()

    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ Clear Chat"):
            reset_system_message()
            st.rerun()
            
    with col_b:
        if st.button("🔒 Logout"):
            st.session_state["api_authenticated"] = False
            st.session_state["api_key"] = ""
            reset_system_message()
            st.rerun()

# 7. Main Dashboard Interface
st.markdown("<div class='main-header'>💼 CareerPulse AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Elevate your resume, pass ATS filters, and land target interviews with executive AI guidance.</div>", unsafe_allow_html=True)

# Display Chat History (skipping raw SystemMessage)
for msg in st.session_state["messages"][1:]:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant", avatar="💼"):
            st.markdown(msg.content)

# Handle Pending Preset Prompts or Chat Input
user_input = st.chat_input("Paste your resume, job description, or career question...")

# Pre-fill input if a preset was clicked
if st.session_state["pending_prompt"]:
    user_input = st.session_state["pending_prompt"]
    st.session_state["pending_prompt"] = None

if user_input:
    # Append user prompt
    st.session_state["messages"].append(HumanMessage(content=user_input))
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Call OpenAI model
    try:
        chat_model = ChatOpenAI(
            model_name=st.session_state["selected_model"],
            temperature=st.session_state["temperature"],
            openai_api_key=st.session_state["api_key"]
        )

        with st.chat_message("assistant", avatar="💼"):
            with st.spinner("Analyzing resume metrics and ATS patterns..."):
                response = chat_model.invoke(st.session_state["messages"])
                st.markdown(response.content)

                # Store response in session memory
                st.session_state["messages"].append(AIMessage(content=response.content))

    except Exception as e:
        st.error(f"An error occurred while communicating with OpenAI API: {e}")