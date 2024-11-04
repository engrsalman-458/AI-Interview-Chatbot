import streamlit as st
from groq import Groq
from io import BytesIO
from gtts import gTTS

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

# Function to synthesize audio using gTTS
def synthesize_audio(text):
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file

# Function to check the user's answer against the correct answer
def check_answer(user_answer, correct_answer):
    if not user_answer.strip():
        return "Please enter a valid answer to receive feedback."
    prompt = f"Evaluate the following answer briefly and indicate if it is correct or not.\n\nUser Answer: {user_answer}\nCorrect Answer: {correct_answer}\nProvide brief feedback if the answer is incorrect."
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content.strip()

# Function to transcribe user's spoken answer
def transcribe_audio(audio_bytes):
    transcription = client.speech.transcribe(audio=audio_bytes, model="whisper-large-v3")
    return transcription.get('text', '').strip()

# Streamlit app for interactive quiz with voice features
def run_quiz():
    st.title("Interactive Quiz App with Voice Support")
    st.write("Enter your field of specialization, listen to the generated question, respond via text or voice, and receive feedback.")

    # User input for specialization
    subject = st.text_input("Field of Specialization")

    # Generate and play the question as audio
    if subject and st.button("Generate Question"):
        question = generate_question(subject)
        st.session_state["question"] = question
        st.session_state["correct_answer"] = generate_correct_answer(question)
        
        # Convert question to audio using gTTS and play
        audio_file = synthesize_audio(question)
        st.audio(audio_file, format="audio/mp3")
        st.write(f"**Question:** {question}")

    # Answer input (text or voice)
    if "question" in st.session_state:
        # User can choose between text and voice input
        user_answer_mode = st.radio("Answer mode", ["Text", "Voice"])

        # Text answer submission
        if user_answer_mode == "Text":
            user_answer = st.text_area("Your Answer")
            if user_answer and st.button("Submit Answer"):
                feedback = check_answer(user_answer, st.session_state["correct_answer"])
                st.write("### Correct Answer:")
                st.write(st.session_state["correct_answer"])
                st.write("### Feedback and Recommendations:")
                st.write(feedback)
        
        # Voice answer submission
        elif user_answer_mode == "Voice":
            audio_upload = st.file_uploader("Upload your answer audio", type=["wav", "mp3"])
            if audio_upload:
                audio_bytes = audio_upload.read()
                user_answer = transcribe_audio(audio_bytes)
                st.write(f"**Transcribed Answer:** {user_answer}")
                feedback = check_answer(user_answer, st.session_state["correct_answer"])
                st.write("### Correct Answer:")
                st.write(st.session_state["correct_answer"])
                st.write("### Feedback and Recommendations:")
                st.write(feedback)

# Run the quiz function in Streamlit
run_quiz()
