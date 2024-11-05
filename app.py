import streamlit as st
from groq import Groq
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

# Custom audio processor for capturing real-time audio
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_data = []

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.audio_data.append(audio)
        return av.AudioFrame.from_ndarray(audio, layout="mono")

    def get_audio_data(self):
        return self.audio_data

# Streamlit app for interactive quiz with real-time audio
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
        
        # Display question
        st.write(f"**Question:** {question}")

    # Check if a question is already generated
    if "question" in st.session_state:
        st.write("Record your answer in real-time:")

        # Real-time audio capture using WebRTC
        webrtc_ctx = webrtc_streamer(
            key="real-time-audio",
            mode=WebRtcMode.SENDRECV,
            audio_processor_factory=AudioProcessor,
            media_stream_constraints={"audio": True, "video": False},
            async_processing=True,
        )

        # Transcribe and evaluate audio answer once recording is complete
        if webrtc_ctx.state.playing:
            processor = webrtc_ctx.audio_processor
            if processor:
                audio_data = processor.get_audio_data()
                if audio_data:
                    st.write("Transcribing your answer...")
                    # Transcribe real-time audio
                    transcription = client.whisper.speech_to_text.create(
                        audio=audio_data,
                        model="whisper-large-v3-turbo",
                    )
                    user_answer = transcription.text.strip()
                    st.write(f"Transcribed Answer: {user_answer}")

                    # Check answer and provide feedback
                    correct_answer = st.session_state["correct_answer"]
                    feedback = check_answer(user_answer, correct_answer)
                    st.write("### Correct Answer:")
                    st.write(correct_answer)
                    st.write("### Feedback and Recommendations:")
                    st.write(feedback)

# Run the quiz function in Streamlit
run_quiz()
