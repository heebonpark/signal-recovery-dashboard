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

        /* ===== Login Landing Page ===== */
        .login-shell {
            max-width: 1120px;
            margin: 48px auto 24px auto;
        }

        @keyframes floatBlob {
            0%, 100% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(20px, -24px) scale(1.08); }
        }

        .hero-panel {
            position: relative;
            height: 100%;
            min-height: 560px;
            border-radius: 28px;
            padding: 3rem 2.5rem;
            background: linear-gradient(155deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%);
            box-shadow: 0 20px 40px -12px rgba(15, 23, 42, 0.45);
            overflow: hidden;
        }

        .hero-blob {
            position: absolute;
            border-radius: 50%;
            filter: blur(50px);
            opacity: 0.35;
            animation: floatBlob 9s ease-in-out infinite;
        }

        .hero-blob-1 {
            width: 260px;
            height: 260px;
            background: #38bdf8;
            top: -60px;
            right: -60px;
        }

        .hero-blob-2 {
            width: 220px;
            height: 220px;
            background: #818cf8;
            bottom: -40px;
            left: -40px;
            animation-delay: 3s;
        }

        .hero-content {
            position: relative;
            z-index: 1;
            color: #f8fafc;
        }

        .hero-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.25);
            padding: 5px 14px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            color: #bfdbfe;
        }

        .hero-content h1 {
            color: #ffffff;
            font-size: 2.6rem;
            margin: 18px 0 10px 0;
            font-weight: 800;
        }

        .hero-sub {
            color: #cbd5e1;
            font-size: 1rem;
            line-height: 1.7;
            margin-bottom: 28px;
        }

        .hero-stats {
            display: flex;
            gap: 28px;
            margin-bottom: 30px;
            padding-bottom: 28px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        }

        .hero-stat strong {
            display: block;
            font-size: 1.9rem;
            font-weight: 800;
            color: #ffffff;
        }

        .hero-stat span {
            font-size: 0.78rem;
            color: #94a3b8;
        }

        .hero-features {
            list-style: none;
            padding: 0;
            margin: 0 0 24px 0;
        }

        .hero-features li {
            color: #e2e8f0;
            font-size: 0.9rem;
            padding: 6px 0 6px 26px;
            position: relative;
        }

        .hero-features li::before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #4ade80;
            font-weight: 800;
        }

        .hero-footnote {
            color: #64748b;
            font-size: 0.78rem;
            margin: 0;
        }

        .login-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.4);
            box-shadow: 0 20px 40px -12px rgba(15, 23, 42, 0.15);
            padding: 2.75rem 2.25rem;
            height: 100%;
        }

        .login-title {
            margin: 0 0 4px 0;
            color: #0f172a;
            font-weight: 800;
        }

        .login-caption {
            color: #64748b;
            font-size: 0.85rem;
            margin-bottom: 20px;
        }

        .login-type-hint {
            background: rgba(37, 99, 235, 0.08);
            border: 1px solid rgba(37, 99, 235, 0.15);
            color: #1e40af;
            font-size: 0.8rem;
            padding: 10px 14px;
            border-radius: 12px;
            margin-bottom: 18px;
        }

        .lockout-banner {
            background: rgba(220, 38, 38, 0.08);
            border: 1px solid rgba(220, 38, 38, 0.25);
            color: #b91c1c;
            font-size: 0.82rem;
            padding: 10px 14px;
            border-radius: 12px;
            margin-bottom: 12px;
        }

        .login-error {
            background: rgba(220, 38, 38, 0.08);
            border: 1px solid rgba(220, 38, 38, 0.25);
            color: #b91c1c;
            font-size: 0.85rem;
            padding: 10px 14px;
            border-radius: 12px;
            margin-top: 4px;
        }

        .security-footnote {
            color: #94a3b8;
            font-size: 0.72rem;
            text-align: center;
            margin: 20px 0 0 0;
            line-height: 1.5;
        }
        </style>
    """, unsafe_allow_html=True)
