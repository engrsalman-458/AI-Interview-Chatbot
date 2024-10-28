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

# Function to generate the correct answer for a given question
def generate_correct_answer(question):
    prompt = f"""
    Provide a correct answer for the following question:
    
    Question: {question}
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Function to check the user's answer against the dynamically generated correct answer and provide feedback
def check_answer(user_answer, correct_answer):
    prompt = f"""
    Evaluate the following answer and indicate whether it is correct or not:

    User Answer: {user_answer}
    Correct Answer: {correct_answer}

    Provide feedback and suggest improvements if the answer is incorrect.
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Streamlit app for interactive quiz
def run_quiz():
    st.title("Interactive Quiz App")
    st.write("Enter your field of specialization, answer the generated question, and get feedback.")

    # User input for specialization
    subject = st.text_input("Field of Specialization")

    # Generate a question based on user input
    if subject and st.button("Generate Question"):
        question = generate_question(subject)
        st.write(f"**Question:** {question}")

        # Dynamically generate the correct answer based on the question
        correct_answer = generate_correct_answer(question)

        # Display the correct answer if needed (for testing)
        st.write("### Correct Answer (for verification):")
        st.write(correct_answer)

        # Answer input box
        user_answer = st.text_area("Your Answer")

        # Submit answer and get feedback
        if user_answer and st.button("Submit Answer"):
            feedback = check_answer(user_answer, correct_answer)

            # Display feedback
            st.write("### Feedback and Recommendations:")
            st.write(feedback)

# Run the quiz function in Streamlit
run_quiz()
