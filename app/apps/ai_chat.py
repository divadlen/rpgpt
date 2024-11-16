import streamlit as st
from streamlit import session_state as state
import time
import anthropic

def main():
    ANTHROPIC_API_KEY = state.get('ANTHROPIC_API_KEY', None)
    if ANTHROPIC_API_KEY is None:
        st.error('Please enter your Anthropic API key in the sidebar')
        return
        
    user_query = st.chat_input('Talk to Claude!')
    if user_query:
        # display the user's message
        with st.chat_message('User'):
            st.markdown(user_query)

        # processing
        with st.status("Downloading data...", expanded=True) as status:
            st.write("Searching for data...")
            time.sleep(2)
            st.write("Found URL.")
            time.sleep(1)
            st.write("Downloading data...")
            time.sleep(1)
            status.update(
                label="Download complete!", state="complete", expanded=False
            )

        st.button("Rerun")



