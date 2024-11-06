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

# Function to convert text to speech using gTTS
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

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
    # Enhanced UI Layout and Style
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>AI Powered Interactive Interview App</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>Generate questions and get feedback on your answers</p>", unsafe_allow_html=True)
    st.write("---")
    
    # User input for specialization
    subject = st.text_input("📝 Enter your Field of Specialization")
    
    # Generate question button and section
    if subject:
        if st.button("🔍 Generate Question"):
            question = generate_question(subject)
            st.session_state["question"] = question
            st.session_state["correct_answer"] = generate_correct_answer(question)
            
            # Display question
            st.markdown(f"<h3 style='color: #0073e6;'>Question</h3>", unsafe_allow_html=True)
            st.write(f"**{question}**")
            
            # Convert question to audio and play it
            audio_data = text_to_speech(question)
            st.audio(audio_data, format="audio/mp3")

    # Answer input and feedback section
    if "question" in st.session_state:
        st.write("---")
        st.markdown("<h3 style='color: #FF6347;'>Your Answer</h3>", unsafe_allow_html=True)
        
        # Answer input box
        user_answer_text = st.text_area("💬 Type your answer here")
        
        # Submit answer button and feedback section
        if user_answer_text and st.button("Submit Answer"):
            correct_answer = st.session_state["correct_answer"]
            feedback = check_answer(user_answer_text.strip(), correct_answer)
            
            st.write("---")
            st.markdown("<h3 style='color: #228B22;'>Correct Answer</h3>", unsafe_allow_html=True)
            st.write(f"**{correct_answer}**")
            st.markdown("<h3 style='color: #DC143C;'>Feedback and Recommendations</h3>", unsafe_allow_html=True)
            st.write(feedback)

# Run the quiz function in Streamlit
run_quiz()
