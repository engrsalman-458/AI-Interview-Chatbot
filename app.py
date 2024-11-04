import streamlit as st
from groq import Groq

# Set up the Groq client using the API key
client = Groq(
    api_key=st.secrets["api_key"]
)

# Function to generate a question based on a specified subject
def generate_question(subject):
    prompt = f"""
    Generate a short, relevant question related to the following subject: {subject}.
    Keep it concise and clear.
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content.strip()

# Function to generate a concise correct answer for a given question
def generate_correct_answer(question):
    prompt = f"""
    Provide a concise answer for the following question:
    
    Question: {question}
    Answer in 1-2 sentences.
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content.strip()

# Function to check the user's answer against the dynamically generated correct answer and provide brief feedback
def check_answer(user_answer, correct_answer):
    # Ensure user answer is not empty before proceeding
    if not user_answer.strip():
        return "Please enter a valid answer to receive feedback."

    prompt = f"""
    Evaluate the following answer briefly and indicate if it is correct or not.

    User Answer: {user_answer}
    Correct Answer: {correct_answer}

    Provide brief feedback if the answer is incorrect.
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content.strip()

# Streamlit app for interactive quiz
def run_quiz():
    st.title("Interactive Quiz App")
    st.write("Enter your field of specialization, answer the generated question, and get feedback.")

    # User input for specialization
    subject = st.text_input("Field of Specialization")

    # Generate a question based on user input
    if subject and st.button("Generate Question"):
        question = generate_question(subject)
        st.session_state["question"] = question  # Store the question in session state
        st.session_state["correct_answer"] = generate_correct_answer(question)  # Generate and store correct answer
        st.write(f"**Question:** {question}")

    # Check if a question is already generated
    if "question" in st.session_state:
        # Answer input box
        user_answer = st.text_area("Your Answer")

        # Submit answer and get feedback
        if user_answer and st.button("Submit Answer"):
            correct_answer = st.session_state["correct_answer"]
            feedback = check_answer(user_answer, correct_answer)

            # Display the correct answer and feedback only after the user has submitted an answer
            st.write("### Correct Answer:")
            st.write(correct_answer)
            st.write("### Feedback and Recommendations:")
            st.write(feedback)

# Run the quiz function in Streamlit
run_quiz()
