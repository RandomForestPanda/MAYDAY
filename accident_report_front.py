import streamlit as st
import requests
import speech_recognition as sr
import base64


def get_image_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_image_base64("image.jpg")
# FastAPI endpoint URL (PORT 8001 for Accident Report Assistant)
API_URL = "http://localhost:8002/search"

st.set_page_config(page_title="Accident Report Query Assistant", layout="centered")
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"]
    {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
    }}
    header {{
    background-color: rgba(0, 0, 0, 0) !important; /* Transparent */
    color: white;
    }}

    h3,p,h4{{
        color: white;  /* Make the text white */
    }}
    [data-testid="stBaseButton-secondary"]
    {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
    }}
    textarea.st-c3.st-cq.st-cr.st-cs.st-ct.st-cu.st-cv.st-cw.st-cx.st-cy.st-b9.st-c5.st-cz.st-d0.st-d1.st-d2.st-d3.st-d4.st-d5.st-d6.st-br.st-bs.st-bt.st-d7.st-bv.st-bw.st-bq.st-d8.st-d9.st-da.st-db.st-dc.st-dd {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
        color: white; /* Ensures text is white */
        border: 1px solid #ccc; /* Optional: adds border */
        padding: 15px; /* Optional: Adjusts padding for better appearance */
        font-size: 16px; /* Optional: adjust font size */
    }}
    textarea.st-c3.st-cq.st-cr.st-cs.st-ct.st-cu.st-cv.st-cw.st-cx.st-cy.st-b9.st-c5.st-cz.st-d0.st-d1.st-d2.st-d3.st-d4.st-d5.st-d6.st-br.st-bs.st-bt.st-d7.st-bv.st-bw.st-bq.st-d8.st-d9.st-da.st-db.st-dc.st-dd::placeholder {{
        color: white !important; /* Ensures placeholder text is also white */
    }}
    /* Style for Unordered Lists (UL) */
    ul {{
        list-style-type: disc; /* Makes sure the bullets are shown */
        color: white; /* Makes the text white */
    }}

    ul li {{
        color: white; /* Ensures the text inside <li> is white */
    }}

    /* Style for Ordered Lists (OL) */
    ol {{
        list-style-type: decimal; /* Makes sure the numbers are shown */
        color: white; /* Makes the text white */
    }}

    ol li {{
        color: white; /* Ensures the text inside <li> is white */
    }}

    /* Style to change the color of list bullets and numbers to white */
    ul li::marker, ol li::marker {{
        color: white; /* Changes the bullet or number to white */
    }}
    </style>
    """, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #D9534F;'>🚨 Accident Report Query Assistant</h1>", unsafe_allow_html=True)


# Initialize session state for speech-to-text
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

# Choose input method
st.markdown("### 🎙️ Choose Input Method")
input_method = st.radio("Select your input method:", ["Text", "Audio"], horizontal=True)

user_query = ""

with st.container():
    if input_method == "Text":
        st.markdown("#### 📝 Enter your query about accident reports:")
        user_query = st.text_area("Type your query here:", value=st.session_state.transcribed_text, placeholder="Enter your query here...")

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
        user_query = st.text_area("Your transcribed text will appear here:", value=st.session_state.transcribed_text, placeholder="Your transcribed text will appear here...")

# Submit Button
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>📋 Get AI Response</h3>", unsafe_allow_html=True)

if st.button("🚀 Get Response", use_container_width=True):
    if user_query:
        try:
            response = requests.post(API_URL, json={"user_id": "user_1", "query": user_query})

            if response.status_code == 200:
                result = response.json().get("response", "No response from server.")
                st.success("✅ AI Response:")
                st.write(result)
            else:
                st.error(f"⚠️ Server Error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Network error: {e}")
    else:
        st.warning("⚠️ Please enter a query.")
