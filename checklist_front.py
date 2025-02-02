import streamlit as st
import requests
import speech_recognition as sr
import time
import base64


def get_image_base64(file):
    with open(file,"rb") as f:
        data=f.read()
    return base64.b64encode(data).decode()
img=get_image_base64("image.jpg")
# Streamlit Frontend - Enhanced UI
st.set_page_config(page_title="Pilot Assistant", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🛫 Pilot Assistant - Mid-Flight Checklist</h1>", unsafe_allow_html=True)
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"]
    {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
    }}
    input.st-ae {{
        background-image: url("data:image/jpeg;base64,{img}");  /* Set the image as background */
        background-size: cover;  /* Ensure the image covers the entire input */
        color: white;  /* White text color */
        border-radius: 8px;  /* Optional: rounded corners */
        padding: 10px;  /* Optional: some padding inside the input */
        border: 1px solid #005b99;  /* Optional: border with a lighter blue color */
        width: 100%;  /* Optional: make the input take full width */
        height: 40px;  /* Optional: set the height of the input */
        font-size: 16px;  /* Optional: set the font size */
    }}
    textarea.st-ae {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
        color: white;  /* White text color */
        border-radius: 8px;  /* Optional: rounded corners */
        padding: 10px;  /* Optional: some padding inside the text area */
        border: 1px solid #005b99;  /* Optional: border with a lighter blue color */
    }}
    input.st-ae::placeholder {{
    color: white;  /* White placeholder text */
    }}
    textarea.st-ae::placeholder {{
    color: white;  /* White placeholder text */
    }}
    button.st-emotion-cache-1vs7lf5 {{
        background-image: url("data:image/jpeg;base64,{img}");  /* Set the image as background */
        background-size: cover;  /* Ensure the image covers the button */
        color: white;  /* White text color */
        border-radius: 8px;  /* Optional: rounded corners */
        padding: 15px 30px;  /* Optional: padding inside the button */
        border: 1px solid #005b99;  /* Optional: border with a lighter blue color */
        font-size: 18px;  /* Optional: font size for text */
        cursor: pointer;  /* Optional: change the cursor to a pointer when hovered */
        text-align: center;  /* Ensure text is centered */
        display: inline-block;  /* Ensure the button behaves like a block element */
        transition: all 0.3s ease;  /* Smooth transition for hover effects */
    }}
    
    button.st-emotion-cache-1vs7lf5:hover {{
        background-color: rgba(0, 0, 0, 0.3);  /* Darken the background on hover */
        border-color: #004b7a;  /* Change the border color on hover */
    }}
    h3, h4 ,p,li{{
        color: white;  /* Make the text white */
    }}
    .st-emotion-cache-1igbibe.ef3psqc19 {{
        background-image: url("data:image/jpeg;base64,{img}"); /* Replace with your image URL */
        background-size: cover; /* Ensure the image covers the entire button */
        color: white; /* Change the text color to white for readability */
        border: none; /* Optional: remove border if you want a clean look */
        padding: 10px 20px; /* Add some padding for better appearance */
        border-radius: 5px; /* Optional: add rounded corners for a modern look */
        text-align: center; /* Ensure the text is centered */
    }}

    .st-emotion-cache-1igbibe.ef3psqc19 p {{
        margin: 0; /* Remove any default margins from the paragraph */
        font-size: 16px; /* Optional: adjust the font size */
    }}
    header {{
    background-color: rgba(0, 0, 0, 0) !important; /* Transparent */
    color: white;
    }}


    </style>
    """, unsafe_allow_html=True)
st.markdown("### ✈️ Enter Flight Details")
user_id = st.text_input("✍️ Enter your User ID", placeholder="e.g., Captain123")

# Choose input method
st.markdown("### 🎙️ Choose Input Method")
input_method = st.radio("", ("Text", "Audio"), horizontal=True)

# Initialize session state for speech-to-text
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

query = ""

# Layout for input sections
with st.container():
    if input_method == "Text":
        st.markdown("#### 📝 Describe your current situation or query:")
        query = st.text_area("", value=st.session_state.transcribed_text, placeholder="Enter details here...")

    elif input_method == "Audio":
        recognizer = sr.Recognizer()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🎤 Start Recording", disabled=st.session_state.is_recording):
                st.session_state.is_recording = True
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    recognizer.pause_threshold = 1.5
                    st.info("🔴 Recording... Speak now.")

                    try:
                        audio = recognizer.listen(source, timeout=30)
                        st.session_state.audio_data = audio
                        st.success("✅ Recording captured. Click 'Stop Recording' to process.")
                    except sr.WaitTimeoutError:
                        st.error("⚠️ No speech detected. Try again.")

        with col2:
            if st.button("⏹️ Stop Recording", disabled=not st.session_state.is_recording):
                st.session_state.is_recording = False
                st.write("⏳ Processing audio...")

                try:
                    transcribed_text = recognizer.recognize_google(st.session_state.audio_data)
                    st.session_state.transcribed_text = transcribed_text
                    st.success("✅ Transcription complete!")
                    st.rerun()
                except sr.UnknownValueError:
                    st.error("⚠️ Sorry, I could not understand the audio.")
                except sr.RequestError:
                    st.error("⚠️ Could not connect to the speech recognition service.")
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")

        # Display transcribed text
        st.markdown("#### 📄 Transcribed Text:")
        query = st.text_area("", value=st.session_state.transcribed_text, placeholder="Your transcribed text will appear here...")

# Submit Button
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>📋 Get Checklist</h3>", unsafe_allow_html=True)

if st.button("🚀 Get Checklist", use_container_width=True):
    if user_id and query:
        try:
            response = requests.post(
                "http://localhost:8001/search",
                json={"user_id": user_id, "query": query},
            )
            if response.status_code == 200:
                answer = response.json().get("response", "No response from server.")
                st.success("✅ Checklist Retrieved:")
                st.markdown(answer)  # Render the response as Markdown
            else:
                st.error(f"⚠️ Server Error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Network error: {e}")
    else:
        st.warning("⚠️ Please provide both User ID and query.")
