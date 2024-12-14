# import streamlit as st
# import hashlib
# import sqlite3
# from langchain_google_genai import ChatGoogleGenerativeAI
# import io
# from gtts import gTTS
# import speech_recognition as sr
# from datetime import datetime
# import pyaudio
# import wave

# # Initialize session state variables
# if 'authenticated' not in st.session_state:
#     st.session_state.authenticated = False
# if 'messages' not in st.session_state:
#     st.session_state.messages = []
# if 'recording' not in st.session_state:
#     st.session_state.recording = False

# def init_db():
#     conn = sqlite3.connect('users.db')
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users
#         (name TEXT, email TEXT PRIMARY KEY, password TEXT, api_key TEXT)
#     ''')
#     conn.commit()
#     conn.close()

# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# def load_css():
#     st.markdown("""
#         <style>
#         /* Main theme colors */
#         :root {
#             --primary-color: #7C4DFF;
#             --secondary-color: #B388FF;
#             --background-color: #F5F7FF;
#             --chat-user: #E3F2FD;
#             --chat-bot: #FFFFFF;
#         }
        
#         /* Global styles */
#         .stApp {
#             background-color: var(--background-color);
#         }
        
#         /* Chat container */
#         .chat-container {
#             background-color: white;
#             border-radius: 20px;
#             padding: 20px;
#             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#             margin-bottom: 20px;
#         }
        
#         /* Message bubbles */
#         .user-message {
#             background-color: var(--chat-user);
#             margin-left: 20%;
#             margin-right: 5%;
#             padding: 15px;
#             border-radius: 20px 20px 5px 20px;
#             margin-bottom: 15px;
#             box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
#             position: relative;
#             animation: slideFromRight 0.3s ease-out;
#         }
        
#         .bot-message {
#             background-color: var(--chat-bot);
#             margin-right: 20%;
#             margin-left: 5%;
#             padding: 15px;
#             border-radius: 20px 20px 20px 5px;
#             margin-bottom: 15px;
#             box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
#             position: relative;
#             animation: slideFromLeft 0.3s ease-out;
#         }
        
#         /* Animations */
#         @keyframes slideFromRight {
#             from { transform: translateX(50px); opacity: 0; }
#             to { transform: translateX(0); opacity: 1; }
#         }
        
#         @keyframes slideFromLeft {
#             from { transform: translateX(-50px); opacity: 0; }
#             to { transform: translateX(0); opacity: 1; }
#         }
        
#         /* Login/Signup container */
#         .auth-container {
#             max-width: 400px;
#             margin: auto;
#             padding: 30px;
#             background: white;
#             border-radius: 20px;
#             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#             animation: fadeIn 0.5s ease-out;
#         }
        
#         @keyframes fadeIn {
#             from { opacity: 0; transform: translateY(20px); }
#             to { opacity: 1; transform: translateY(0); }
#         }
        
#         /* Buttons */
#         .stButton button {
#             background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
#             color: white;
#             border-radius: 25px;
#             padding: 10px 25px;
#             border: none;
#             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#             transition: transform 0.2s, box-shadow 0.2s;
#         }
        
#         .stButton button:hover {
#             transform: translateY(-2px);
#             box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
#         }
        
#         /* Input fields */
#         .stTextInput input {
#             border-radius: 15px;
#             border: 2px solid #E0E0E0;
#             padding: 12px 20px;
#             transition: border-color 0.3s;
#         }
        
#         .stTextInput input:focus {
#             border-color: var(--primary-color);
#             box-shadow: 0 0 0 2px rgba(124, 77, 255, 0.2);
#         }
        
#         /* Sidebar */
#         .sidebar {
#             background-color: white;
#             padding: 20px;
#             border-radius: 20px;
#             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         }
        
#         /* Voice recording button */
#         .voice-button {
#             background-color: var(--primary-color);
#             color: white;
#             border-radius: 50%;
#             width: 60px;
#             height: 60px;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             cursor: pointer;
#             transition: all 0.3s;
#         }
        
#         .voice-indicator {
#             position: fixed;
#             bottom: 100px;
#             left: 50%;
#             transform: translateX(-50%);
#             background-color: rgba(0, 0, 0, 0.8);
#             color: white;
#             padding: 10px 20px;
#             border-radius: 20px;
#             z-index: 1000;
#             display: flex;
#             align-items: center;
#             gap: 10px;
#         }
        
#         .recording-dot {
#             width: 12px;
#             height: 12px;
#             background-color: #FF4444;
#             border-radius: 50%;
#             animation: pulse 1s infinite;
#         }
        
#         .voice-button:hover {
#             transform: scale(1.1);
#         }
        
#         .voice-button.recording {
#             background-color: #FF5252;
#             animation: pulse 1.5s infinite;
#         }
        
#         @keyframes pulse {
#             0% { transform: scale(1); }
#             50% { transform: scale(1.1); }
#             100% { transform: scale(1); }
#         }
        
#         /* Message timestamp */
#         .message-time {
#             font-size: 0.8em;
#             color: #757575;
#             margin-top: 5px;
#         }
#         </style>
#     """, unsafe_allow_html=True)

# def record_audio():
#     r = sr.Recognizer()
#     # Adjust for ambient noise before recording
#     with sr.Microphone() as source:
#         r.adjust_for_ambient_noise(source, duration=0.5)
#         st.info("🎤 Listening... Speak now!")
#         try:
#             # Reduce timeout and add phrase_time_limit for faster response
#             audio = r.listen(source, timeout=3, phrase_time_limit=10)
#             st.info("Processing...")
#             # Use Google Speech Recognition with language specification
#             text = r.recognize_google(audio, language='en-US')
#             return text
#         except sr.UnknownValueError:
#             st.warning("Could not understand audio")
#             return None
#         except sr.RequestError:
#             st.error("Could not request results")
#             return None
#         except sr.WaitTimeoutError:
#             st.warning("No speech detected")
#             return None

# def update_api_key(new_api_key):
#     conn = sqlite3.connect('users.db')
#     c = conn.cursor()
#     c.execute("UPDATE users SET api_key = ? WHERE email = ?", 
#              (new_api_key, st.session_state.user['email']))
#     conn.commit()
#     conn.close()
#     st.session_state.user['api_key'] = new_api_key
#     return True

# def settings_sidebar():
#     with st.sidebar:
#         st.markdown("""
#             <div class='sidebar'>
#                 <h2>Settings</h2>
#                 <div class='user-info'>
#                     <p>👤 {}</p>
#                     <p>📧 {}</p>
#                 </div>
#             </div>
#         """.format(st.session_state.user['name'], st.session_state.user['email']), 
#         unsafe_allow_html=True)
        
#         st.subheader("🔑 Update API Key")
#         new_api_key = st.text_input("New API Key", type="password", key="new_api_key")
#         if st.button("Update", key="update_api"):
#             if new_api_key:
#                 if update_api_key(new_api_key):
#                     st.success("✅ API Key updated!")
#                 else:
#                     st.error("Failed to update API Key")
#             else:
#                 st.warning("Please enter a new API Key")
        
#         st.markdown("---")
#         if st.button("🚪 Logout", key="sidebar_logout"):
#             st.session_state.authenticated = False
#             st.session_state.messages = []
#             st.rerun()

# def login():
#     st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
#     st.title("🔐 Login")
#     email = st.text_input("📧 Email", key="login_email")
#     password = st.text_input("🔒 Password", type="password", key="login_password")
    
#     if st.button("Login", key="login_button"):
#         if email and password:
#             conn = sqlite3.connect('users.db')
#             c = conn.cursor()
#             c.execute("SELECT * FROM users WHERE email=? AND password=?", 
#                      (email, hash_password(password)))
#             user = c.fetchone()
#             conn.close()
            
#             if user:
#                 st.session_state.authenticated = True
#                 st.session_state.user = {
#                     'name': user[0],
#                     'email': user[1],
#                     'api_key': user[3]
#                 }
#                 st.success("✨ Welcome back!")
#                 st.rerun()
#             else:
#                 st.error("❌ Invalid credentials!")
#         else:
#             st.warning("⚠️ Please fill all fields!")
#     st.markdown("</div>", unsafe_allow_html=True)

# def signup():
#     st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
#     st.title("📝 Sign Up")
#     name = st.text_input("👤 Name", key="signup_name")
#     email = st.text_input("📧 Email", key="signup_email")
#     password = st.text_input("🔒 Password", type="password", key="signup_password")
#     api_key = st.text_input("🔑 Google API Key", type="password", key="signup_api_key")
    
#     if st.button("Sign Up", key="signup_button"):
#         if name and email and password and api_key:
#             conn = sqlite3.connect('users.db')
#             c = conn.cursor()
#             hashed_pwd = hash_password(password)
#             try:
#                 c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", 
#                          (name, email, hashed_pwd, api_key))
#                 conn.commit()
#                 st.success("✨ Account created successfully!")
#             except sqlite3.IntegrityError:
#                 st.error("❌ Email already exists!")
#             conn.close()
#         else:
#             st.warning("⚠️ Please fill all fields!")
#     st.markdown("</div>", unsafe_allow_html=True)

# def chat_interface():
#     settings_sidebar()
#     st.title("💬 AI Chat Assistant")
    
#     # Initialize LLM
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-1.5-pro",
#         google_api_key=st.session_state.user['api_key'],
#         temperature=0.7,
#         max_tokens=None,
#         timeout=None,
#         max_retries=2
#     )
    
#     # Display chat messages
#     st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
#     for message in st.session_state.messages:
#         timestamp = datetime.now().strftime("%H:%M")
#         if message["role"] == "user":
#             st.markdown(f"""
#                 <div class='user-message'>
#                     {message['content']}
#                     <div class='message-time'>{timestamp}</div>
#                 </div>
#             """, unsafe_allow_html=True)
#         else:
#             st.markdown(f"""
#                 <div class='bot-message'>
#                     {message['content']}
#                     <div class='message-time'>{timestamp}</div>
#                 </div>
#             """, unsafe_allow_html=True)
#             if 'audio' in message:
#                 st.audio(message['audio'], format='audio/mp3')
#     st.markdown("</div>", unsafe_allow_html=True)
    
#     # Input section
#     col1, col2, col3 = st.columns([6, 1, 1])
    
#     with col1:
#         user_input = st.text_input("Message", key="chat_input", 
#                                  placeholder="Type your message here...")
    
#     with col2:
#         if st.button("🎤", key="voice_button", 
#                     help="Click to record voice message"):
#             voice_input = record_audio()
#             if voice_input:
#                 # Automatically process voice input
#                 # Add user message
#                 st.session_state.messages.append({
#                     "role": "user",
#                     "content": voice_input,
#                     "type": "voice"
#                 })
                
#                 # Get bot response with reduced temperature for faster response
#                 llm.temperature = 0.3  # Reduce temperature for faster responses
#                 response = llm.invoke(voice_input)
#                 response_text = response.content
                
#                 # Convert to speech in a more optimized way
#                 tts = gTTS(text=response_text, lang='en', slow=False)
#                 audio_fp = io.BytesIO()
#                 tts.write_to_fp(audio_fp)
#                 audio_fp.seek(0)
                
#                 # Add bot response
#                 st.session_state.messages.append({
#                     "role": "assistant",
#                     "content": response_text,
#                     "audio": audio_fp,
#                     "type": "voice"
#                 })
                
#                 st.rerun()
    
#     with col3:
#         if st.button("Send", key="send_button"):
#             if user_input:
#                 # Add user message
#                 st.session_state.messages.append({
#                     "role": "user",
#                     "content": user_input
#                 })
                
#                 # Get bot response
#                 response = llm.invoke(user_input)
#                 response_text = response.content
                
#                 # Convert to speech
#                 tts = gTTS(text=response_text, lang='en')
#                 audio_fp = io.BytesIO()
#                 tts.write_to_fp(audio_fp)
#                 audio_fp.seek(0)
                
#                 # Add bot response
#                 st.session_state.messages.append({
#                     "role": "assistant",
#                     "content": response_text,
#                     "audio": audio_fp
#                 })
                
#                 st.rerun()

# def main():
#     load_css()
#     init_db()
    
#     if not st.session_state.authenticated:
#         tab1, tab2 = st.tabs(["Login", "Sign Up"])
#         with tab1:
#             login()
#         with tab2:
#             signup()
#     else:
#         chat_interface()

# if __name__ == "__main__":
#     main()


import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import sqlite3
import hashlib
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
import time
from langchain_groq import ChatGroq

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False

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

# Voice handling function
def record_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... (Speak now)")
        r.adjust_for_ambient_noise(source, duration=0.2)
        try:
            audio = r.listen(source, timeout=3, phrase_time_limit=10)
            st.info("Processing...")
            text = r.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            st.warning("No speech detected")
            return None
        except sr.UnknownValueError:
            st.warning("Could not understand audio")
            return None
        except sr.RequestError:
            st.error("Could not request results")
            return None

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
        
        .recording-indicator {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
        }
        
        .pulse-dot {
            width: 12px;
            height: 12px;
            background-color: #FF4444;
            border-radius: 50%;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.8; }
            100% { transform: scale(1); opacity: 1; }
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
    st.title("💬 AI Voice Chat")
    
    # Display chat messages
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
                <div class='user-message'>
                    {message['content']}
                    <div style='font-size: 0.8em; color: #666;'>{message['timestamp']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='bot-message'>
                    {message['content']}
                    <div style='font-size: 0.8em; color: #666;'>{message['timestamp']}</div>
                </div>
            """, unsafe_allow_html=True)
            if 'audio' in message:
                st.audio(message['audio'], format='audio/mp3')
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat inputs
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        user_input = st.text_input("Message", key="text_input", 
                                 placeholder="Type or click microphone to speak...")
    
    with col2:
        if st.button("🎤", key="voice_button"):
            voice_input = record_audio()
            if voice_input:
                user_input = voice_input
    
    with col3:
        if st.button("Send", key="send_button") or user_input:
            if user_input:
                # Initialize LLM
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro",
                    google_api_key=st.session_state.user['api_key'],
                    temperature=0.3,
                    max_tokens=None,
                    timeout=None,
                    max_retries=2
                )
                # apikey="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"
                # llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768",api_key=apikey)
                
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
                # Get bot response
                response = llm.invoke(user_input)
                response_text = response.content
                
                # Convert to speech
                tts = gTTS(text=response_text, lang='en', slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                
                # Add bot response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "audio": audio_fp,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
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