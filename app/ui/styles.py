import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* Pretendard Web Font */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        html, body, [class*="css"] {
            font-family: 'Pretendard', sans-serif;
            background-color: #f8fafc;
        }
        
        /* Hide Default Streamlit Elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Premium Data Intel PRO Styling */
        .stApp {
            background: linear-gradient(to right bottom, #e2e8f0, #ffffff);
        }
        
        h1, h2, h3 {
            color: #0f172a; /* Dark Navy */
        }
        
        .stButton>button {
            background-color: #2563eb; /* Royal Blue */
            color: white;
            border-radius: 12px;
            border: none;
            padding: 0.5rem 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: #1d4ed8;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }
        
        .stTextInput>div>div>input {
            border-radius: 12px;
            border: 1px solid #cbd5e1;
            padding: 0.5rem 1rem;
            color: #334155;
            background-color: rgba(255, 255, 255, 0.8);
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
        }
        
        /* Glassmorphism Container */
        .glass-container {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            border-left: 4px solid #2563eb;
        }

        .metric-card h4 {
            margin: 0;
            color: #64748b;
            font-size: 0.85rem;
            font-weight: 500;
        }

        .metric-card h2 {
            margin: 4px 0 0 0;
            color: #0f172a !important;
        }

        .badge {
            display: inline-block;
            background: rgba(37, 99, 235, 0.1);
            color: #2563eb;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-right: 8px;
            vertical-align: middle;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 12px 12px 0 0;
            padding: 0.5rem 1.25rem;
        }

        [data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
        }
        </style>
    """, unsafe_allow_html=True)
