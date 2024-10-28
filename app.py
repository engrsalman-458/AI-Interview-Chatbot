import streamlit as st
from groq import Groq

# Set up the Groq client using the API key
client = Groq(
    api_key = st.secrets["api_key"]
)

# Function to generate a question based on a specified subject
def generate_question(subject):
    prompt = f"""
    Generate a question related to the following subject: {subject}.
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Function to check the user's answer against the expected answer
def check_answer(user_answer, correct_answer):
    prompt = f"""
    Evaluate the following answer and indicate whether it is correct or not:

    User Answer: {user_answer}
    Correct Answer: {correct_answer}

    Provide feedback on the user's answer.
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Streamlit app for interactive quiz
def run_quiz():
    st.title("Interactive Quiz App")
    st.write("Enter your field of specialization and answer the generated questions.")

    # User input for specialization
    subject = st.text_input("Field of Specialization")

    if subject:
        if st.button("Generate Question"):
            question = generate_question(subject)
            st.write(f"Question: {question}")

            # Answer input box
            user_answer = st.text_area("Your Answer")

            if st.button("Submit Answer"):
                # Placeholder correct answer; replace with actual expected answers if available
                correct_answer = "This is a placeholder answer."

                # Check answer and provide feedback
                feedback = check_answer(user_answer, correct_answer)
                st.write("Feedback on Your Answer:")
                st.write(feedback)

# Run the quiz function in Streamlit
run_quiz()
