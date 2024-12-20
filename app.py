import streamlit as st
from groq import Groq
from io import BytesIO
from gtts import gTTS
import sounddevice as sd
import numpy as np
import tempfile
import wave

# Set up the Groq client using the API key
client = Groq(api_key=st.secrets["api_key"])

# Function to generate a question based on a specified subject
def generate_question(subject):
    prompt = f"Generate a short, relevant question related to the following subject: {subject}. Keep it concise and clear."
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content.strip()

# Function to generate a concise correct answer for a given question
def generate_correct_answer(question):
    prompt = f"Provide a concise answer for the following question:\n\nQuestion: {question}\nAnswer in 1-2 sentences."
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content.strip()

# Function to convert text to speech using gTTS
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

# Function to transcribe audio to text using Groq model
def transcribe_audio(audio_data):
    audio_bytes = audio_data.read()
    response = client.speech_to_text.create(
        audio=audio_bytes,
        model="groq-8b-speech",
    )
    return response["transcription"]

# Function to capture audio input from microphone
def record_audio(duration=5, fs=44100):
    st.write("Recording... Speak now!")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    audio = np.squeeze(audio)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        with wave.open(tmpfile.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())
        return tmpfile.name

# Function to check the user's answer against the dynamically generated correct answer and provide brief feedback
def check_answer(user_answer, correct_answer):
    if not user_answer.strip():
        return "Please enter a valid answer to receive feedback."

    prompt = f"Evaluate the following answer briefly and indicate if it is correct or not.\n\nUser Answer: {user_answer}\nCorrect Answer: {correct_answer}\n\nProvide brief feedback if the answer is incorrect."
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content.strip()

# Streamlit app for interactive quiz
def run_quiz():
    st.title("AI Powered Interactive Interview App")
    st.write("Enter your field of specialization, answer the generated question, and get feedback.")

    # Enhanced UI Layout and Style
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>AI Powered Interactive Interview App</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>Generate questions and get feedback on your answers</p>", unsafe_allow_html=True)
    st.write("---")
    
    # User input for specialization
    subject = st.text_input("Field of Specialization")

    # Generate a question and provide voice output
    if subject and st.button("Generate Question"):
        question = generate_question(subject)
        st.session_state["question"] = question
        st.session_state["correct_answer"] = generate_correct_answer(question)
        
        # Display question and convert to audio
        st.write(f"**Question:** {question}")
        audio_data = text_to_speech(question)
        st.audio(audio_data, format="audio/mp3")
    
    # Check if a question is already generated
    if "question" in st.session_state:
        st.write("---")
        st.markdown("<h3 style='color: #FF6347;'>Your Answer</h3>", unsafe_allow_html=True)
        
        # Answer input box
        user_answer_text = st.text_area("💬 Type your answer here")
        
        # Option to record voice response
        if st.button("🎤 Record Answer (5 seconds)"):
            audio_file_path = record_audio()
            with open(audio_file_path, "rb") as audio_file:
                transcribed_text = transcribe_audio(audio_file)
            st.write("**Transcribed Answer:**", transcribed_text)
            user_answer_text = transcribed_text

        # Submit answer and get feedback
        if user_answer_text and st.button("Submit Answer"):
            correct_answer = st.session_state["correct_answer"]
            feedback = check_answer(user_answer_text.strip(), correct_answer)
            st.markdown("<h3 style='color: #228B22;'>Correct Answer</h3>", unsafe_allow_html=True)
            st.write(f"**{correct_answer}**")
            st.markdown("<h3 style='color: #DC143C;'>Feedback and Recommendations</h3>", unsafe_allow_html=True)
            st.write(feedback)

# Run the quiz function in Streamlit
run_quiz()
