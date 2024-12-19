import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Database functions
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            name TEXT,
            email TEXT PRIMARY KEY,
            password TEXT,
            api_key TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(name, email, password, api_key):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (name, email, password, api_key) VALUES (?, ?, ?, ?)",
            (name, email, hash_password(password), api_key)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(email, password):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    user = c.fetchone()
    conn.close()
    return user

def update_api_key(email, new_api_key):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET api_key=? WHERE email=?",
        (new_api_key, email)
    )
    conn.commit()
    conn.close()

# UI Styling
def load_css():
    st.markdown("""
        <style>
        /* Main theme colors */
        :root {
            --primary-color: #7C4DFF;
            --secondary-color: #B388FF;
            --background-color: #F5F7FF;
            --chat-user: #E3F2FD;
            --chat-bot: #FFFFFF;
        }
        
        .stApp {
            background-color: var(--background-color);
        }
        
        .chat-container {
            background-color: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        .user-message {
            background-color: var(--chat-user);
            margin-left: 20%;
            margin-right: 5%;
            padding: 15px;
            border-radius: 20px 20px 5px 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            animation: slideFromRight 0.3s ease-out;
        }
        
        .bot-message {
            background-color: var(--chat-bot);
            margin-right: 20%;
            margin-left: 5%;
            padding: 15px;
            border-radius: 20px 20px 20px 5px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            animation: slideFromLeft 0.3s ease-out;
        }
        
        @keyframes slideFromRight {
            from { transform: translateX(50px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideFromLeft {
            from { transform: translateX(-50px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .auth-container {
            max-width: 400px;
            margin: auto;
            padding: 30px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stButton button {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: 25px;
            padding: 10px 25px;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
        }
        
        .stTextInput input {
            border-radius: 15px;
            border: 1px solid #E0E0E0;
            padding: 10px 15px;
        }
        </style>
    """, unsafe_allow_html=True)

def login_page():
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.title("🔐 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", key="login_button"):
        if email and password:
            user = get_user(email, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = {
                    'name': user[0],
                    'email': user[1],
                    'api_key': user[3]
                }
                st.success("✨ Welcome back!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials!")
        else:
            st.warning("⚠️ Please fill all fields!")
    st.markdown("</div>", unsafe_allow_html=True)

def signup_page():
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.title("📝 Sign Up")
    name = st.text_input("Name", key="signup_name")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    api_key = st.text_input("Google API Key", type="password", key="signup_api_key")
    
    if st.button("Sign Up", key="signup_button"):
        if name and email and password and api_key:
            if save_user(name, email, password, api_key):
                st.success("✨ Account created successfully!")
            else:
                st.error("❌ Email already exists!")
        else:
            st.warning("⚠️ Please fill all fields!")
    st.markdown("</div>", unsafe_allow_html=True)

def settings_sidebar():
    with st.sidebar:
        st.title("⚙️ Settings")
        st.write(f"👤 Logged in as: {st.session_state.user['name']}")
        
        new_api_key = st.text_input(
            "Update API Key",
            type="password",
            key="update_api_key"
        )
        
        if st.button("Update API Key"):
            if new_api_key:
                update_api_key(st.session_state.user['email'], new_api_key)
                st.session_state.user['api_key'] = new_api_key
                st.success("✅ API Key updated!")
                st.rerun()
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.rerun()

def chat_interface():
    settings_sidebar()
    st.title("💬 AI Chat Assistant")
    
    # Display chat messages
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
                <div class='user-message'>
                    {message['content']}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='bot-message'>
                    {message['content']}
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat input with container to prevent auto-rerun
    with st.container():
        user_input = st.text_input("Message", key="text_input", 
                                  placeholder="Type your message...")
        # Clear input after sending
        if st.session_state.get('clear_input', False):
            st.session_state.text_input = ""
            st.session_state.clear_input = False
    
    # Handle input and generate response
    if st.button("Send", key="send_button"):
        if user_input and user_input.strip():
            # Initialize LLM with faster response settings
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=st.session_state.user['api_key'],
                temperature=0.1,  # Lower temperature for more focused responses
                max_tokens=150,   # Limit response length
                timeout=10,       # Shorter timeout
                max_retries=1     # Fewer retries for faster failure
            )
            
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            try:
                # Get bot response with timeout
                response = llm.invoke(user_input)
                response_text = response.content
                
                # Add bot response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
            except Exception as e:
                st.error("Failed to get response. Please try again.")
            
            st.rerun()

def main():
    load_css()
    init_db()
    
    if not st.session_state.authenticated:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            login_page()
        with tab2:
            signup_page()
    else:
        chat_interface()

if __name__ == "__main__":
    main()
