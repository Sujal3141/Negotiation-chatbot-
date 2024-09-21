import re
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from textblob import TextBlob  


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])


st.set_page_config(page_title="Negotiation Chatbot")
st.header("Negotiation Chatbot using Gemini LLM")


if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'bot_offer' not in st.session_state:
    st.session_state['bot_offer'] = 90  # Example starting offer
if 'negotiation_ongoing' not in st.session_state:
    st.session_state['negotiation_ongoing'] = True


def negotiate_price(user_offer):
    bot_offer = st.session_state['bot_offer']
    
    # Simple negotiation logic
    if user_offer >= bot_offer:
        return f"Accepted! The final price is ${user_offer}."
    elif bot_offer - user_offer <= 10:
        st.session_state['bot_offer'] = user_offer 
        return f"Close enough! Let's settle at ${user_offer}."
    else:
        st.session_state['bot_offer'] -= 10 
        return f"I can offer ${st.session_state['bot_offer']}. How about that?"


def extract_number_from_text(text):
    match = re.search(r'\d+', text) 
    if match:
        return float(match.group())
    return None


def is_rejection(user_input):
    rejection_keywords = ['cannot', "won't", 'not', 'no', 'reject']
    return any(keyword in user_input.lower() for keyword in rejection_keywords)


user_input = st.text_input("Your offer:", key="input")
submit = st.button("Submit")


if submit and user_input:
   
    if is_rejection(user_input):
        bot_response = "It seems you're not happy with my offer. How about a lower price?"
        st.session_state['bot_offer'] -= 10
        bot_response += f" I can offer ${st.session_state['bot_offer']}. How about that?"
    else:
        
        user_offer = extract_number_from_text(user_input)
        if user_offer is not None:
            bot_response = negotiate_price(user_offer)
            if "Accepted" in bot_response:
                st.session_state['negotiation_ongoing'] = False
        else:
            bot_response = "Please provide a valid number for your offer."

    st.session_state['chat_history'].append(("You", user_input))
    st.session_state['chat_history'].append(("Bot", bot_response))

    for role, text in st.session_state["chat_history"]:
        st.write(f"{role}: {text}")
