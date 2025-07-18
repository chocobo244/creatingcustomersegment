"""
Main Streamlit application for Multi-Touch Attribution Platform.
"""
import streamlit as st
import asyncio
from typing import Dict, Any

from frontend.pages import (
    dashboard,
    data_ingestion,
    attribution_analysis,
    channel_performance,
    customer_journey,
    settings as settings_page
)
from frontend.utils.api_client import APIClient
from frontend.utils.auth import check_authentication
from config.settings import get_streamlit_settings


# Configure Streamlit page
settings = get_streamlit_settings()

st.set_page_config(
    page_title=settings.title,
    page_icon=settings.page_icon,
    layout=settings.layout,
    initial_sidebar_state=settings.initial_sidebar_state
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #FF6B6B;
    }
    
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .nav-item {
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 0.25rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .nav-item:hover {
        background-color: #f0f0f0;
    }
    
    .nav-item.active {
        background-color: #FF6B6B;
        color: white;
    }
    
    .status-success {
        color: #28a745;
        font-weight: 600;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: 600;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'
    
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}


def render_sidebar():
    """Render the application sidebar with navigation."""
    with st.sidebar:
        st.markdown('<div class="sidebar-header">📊 Attribution Analytics</div>', 
                   unsafe_allow_html=True)
        
        # API Status
        st.markdown("### 🔗 API Status")
        try:
            # Test API connection
            status = asyncio.run(st.session_state.api_client.check_health())
            if status:
                st.markdown('<span class="status-success">🟢 Connected</span>', 
                           unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-error">🔴 Disconnected</span>', 
                           unsafe_allow_html=True)
        except Exception:
            st.markdown('<span class="status-error">🔴 Error</span>', 
                       unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        pages = {
            "📈 Dashboard": "Dashboard",
            "📥 Data Ingestion": "Data Ingestion", 
            "🎯 Attribution Analysis": "Attribution Analysis",
            "📺 Channel Performance": "Channel Performance",
            "🛤️ Customer Journey": "Customer Journey",
            "⚙️ Settings": "Settings"
        }
        
        for display_name, page_name in pages.items():
            if st.button(display_name, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()
        
        st.markdown("---")
        
        # User info and actions
        if st.session_state.authenticated:
            st.markdown("### 👤 User")
            st.write(f"Logged in as: **{st.session_state.user_data.get('username', 'User')}**")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_data = {}
                st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            Multi-Touch Attribution Platform<br>
            Version 1.0.0
        </div>
        """, unsafe_allow_html=True)


def render_main_content():
    """Render the main content area based on current page."""
    current_page = st.session_state.current_page
    
    # Page routing
    if current_page == "Dashboard":
        dashboard.render()
    elif current_page == "Data Ingestion":
        data_ingestion.render()
    elif current_page == "Attribution Analysis":
        attribution_analysis.render()
    elif current_page == "Channel Performance":
        channel_performance.render()
    elif current_page == "Customer Journey":
        customer_journey.render()
    elif current_page == "Settings":
        settings_page.render()
    else:
        st.error(f"Unknown page: {current_page}")


def render_login_page():
    """Render the login page."""
    st.markdown('<h1 class="main-header">Multi-Touch Attribution Platform</h1>', 
               unsafe_allow_html=True)
    
    st.markdown("### 🔐 Please login to continue")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                # For demo purposes, accept any non-empty credentials
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.user_data = {
                        'username': username,
                        'login_time': st.session_state.get('timestamp', 'now')
                    }
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Please enter both username and password")
        
        # Demo credentials info
        st.info("**Demo Mode**: Enter any username and password to continue")


def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Render authenticated application
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main()