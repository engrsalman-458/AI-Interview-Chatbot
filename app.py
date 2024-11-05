import streamlit as st
from groq import Groq
from io import BytesIO
from gtts import gTTS
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av

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

# Function to transcribe audio to text using Groq's Whisper model
def transcribe_audio(audio_data):
    transcription = client.whisper.speech_to_text.create(
        audio=audio_data,
        model="whisper-large-v3-turbo",
    )
    return transcription.text.strip()

# Audio processor class for real-time voice input
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_data = []

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.audio_data.append(audio)
        return av.AudioFrame.from_ndarray(audio, layout="mono")

    def get_audio_data(self):
        return self.audio_data

# Streamlit app for interactive quiz
def run_quiz():
    st.title("Interactive Voice Quiz App")
    st.write("Enter your field of specialization, answer the generated question, and get feedback.")

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
        st.write("Record your answer in real-time or type it below:")
        
        # Real-time audio recording setup
        webrtc_ctx = webrtc_streamer(
            key="real-time-audio",
            mode=WebRtcMode.SENDRECV,
            audio_processor_factory=AudioProcessor,
            media_stream_constraints={"audio": True, "video": False},
            async_processing=True,
        )

        # Text area for optional text-based answer
        user_answer_text = st.text_area("Or type your answer here:")

        # Process recorded answer
        user_answer = ""
        if webrtc_ctx.state.playing:
            processor = webrtc_ctx.audio_processor
            if processor:
                audio_data = processor.get_audio_data()
                if audio_data:
                    st.write("Transcribing your answer...")
                    user_answer = transcribe_audio(audio_data)
                    st.write(f"Transcribed Answer: {user_answer}")
        elif user_answer_text:
            user_answer = user_answer_text.strip()

        # Submit answer and get feedback
        if user_answer and st.button("Submit Answer"):
            correct_answer = st.session_state["correct_answer"]
            feedback = check_answer(user_answer, correct_answer)
            st.write("### Correct Answer:")
            st.write(correct_answer)
            st.write("### Feedback and Recommendations:")
            st.write(feedback)

# Run the quiz function in Streamlit
run_quiz()
