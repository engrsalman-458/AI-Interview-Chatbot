import streamlit as st
from groq import Groq
import requests  # For handling any API calls to the venue database

# Set up the Groq client using the API key
client = Groq(api_key=st.secrets["api_key"])

# Sample venue database query function (stubbed)
def query_venues(criteria):
    """
    Query the venue database using criteria and return a list of venues.
    Replace with actual code to query your database.
    """
    # For demonstration, returns mock data
    return [
        {"name": "Elegant Banquet Hall", "location": "Downtown", "capacity": 150, "amenities": ["Catering", "Wi-Fi", "Parking"]},
        {"name": "Seaside Pavilion", "location": "Beachfront", "capacity": 80, "amenities": ["Outdoor", "Beach access", "Live Music"]},
        # Add more mock or actual data as needed
    ]

# Function to generate a venue recommendation prompt for Groq LLM
def generate_recommendation_prompt(user_preferences):
    prompt = f"""
    Based on the following preferences, recommend suitable venues:
    Event Type: {user_preferences.get("event_type")}
    Location: {user_preferences.get("location")}
    Guest Count: {user_preferences.get("guest_count")}
    Ambiance: {user_preferences.get("ambiance")}
    Additional Amenities: {user_preferences.get("amenities")}
    """
    return prompt.strip()

# Function to get venue recommendations from Groq LLM
def get_venue_recommendations(preferences):
    prompt = generate_recommendation_prompt(preferences)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )
    return chat_completion.choices[0].message.content.strip()

# Streamlit app interface for venue recommendation
def run_venue_recommendation_app():
    st.title("AI Venue Recommendation Chatbot")
    st.subheader("Personalized Recommendations Based on Your Event Needs")

    # User input for event preferences
    user_preferences = {}
    user_preferences["event_type"] = st.selectbox("Type of Event", ["Wedding", "Corporate", "Party", "Other"])
    user_preferences["location"] = st.text_input("Preferred Location")
    user_preferences["guest_count"] = st.number_input("Estimated Guest Count", min_value=1, step=1)
    user_preferences["ambiance"] = st.selectbox("Preferred Ambiance", ["Indoor", "Outdoor", "Beachfront", "Rustic", "Modern"])
    user_preferences["amenities"] = st.multiselect("Additional Amenities", ["Catering", "Wi-Fi", "Parking", "Audio-Visual", "Live Music"])

    # Button to generate venue recommendations
    if st.button("Get Recommendations"):
        # Get relevant venues based on preferences
        venues = query_venues(user_preferences)  # Replace with actual database query
        if venues:
            # Retrieve personalized recommendations using Groq LLM
            recommendations = get_venue_recommendations(user_preferences)
            st.write("### Recommended Venues:")
            st.write(recommendations)

            # Display venue information
            for venue in venues:
                st.write(f"**{venue['name']}**")
                st.write(f"Location: {venue['location']}")
                st.write(f"Capacity: {venue['capacity']} guests")
                st.write(f"Amenities: {', '.join(venue['amenities'])}")
        else:
            st.write("No venues match your preferences. Please try adjusting your criteria.")

# Run the venue recommendation app in Streamlit
run_venue_recommendation_app()
