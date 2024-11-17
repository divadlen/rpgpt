import streamlit as st
from streamlit import session_state as state
import time

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage

from utils.ai_methods import stream_llm_response

CONTEXT_LIMIT = 10

def main():
    if state['selected_model'] in [None, ""]:
        st.error('Please input your API key and select a model')
        return

    state['chat_history'] = state.get('chat_history', [])

    mascot = 'Agent'
    model_provider = state['selected_model'].split("/")[0]
    if model_provider == "openai":
        llm_stream = ChatOpenAI(
            api_key=state['OPENAI_API_KEY'],
            model_name=state['selected_model'].split("/")[1],
            temperature=0.3,
            streaming=True,
        )
        mascot = 'OpenAI'
    elif model_provider == "anthropic":
        llm_stream = ChatAnthropic(
            api_key=state['ANTHROPIC_API_KEY'],
            model=state['selected_model'].split("/")[1],
            temperature=0.3,
            streaming=True,
        )
        mascot = 'Claude'

    with st.sidebar:
        clear_chat_history = st.button('Clear Chat History', type='primary')
        if clear_chat_history:
            state['chat_history'] = []
            st.experimental_fragment()


    # Display the chat history with separate expanders for each interaction
    user_messages = [msg for msg in state['chat_history'] if msg['role'] == 'user']
    assistant_messages = [msg for msg in state['chat_history'] if msg['role'] == 'assistant']

    # Determine the range for interactions (based on the smaller list to avoid mismatches)
    interaction_count = min(len(user_messages), len(assistant_messages))

    # Display the chat history, starting with the oldest messages
    st.info(f"Showing only up to {CONTEXT_LIMIT} messages")
    for i in range(interaction_count):
        user_message = user_messages[i]
        assistant_message = assistant_messages[i]

        with st.expander(f"Interaction {i + 1}", expanded=False):
            with st.chat_message('User'):
                st.markdown(user_message['content'])
            with st.chat_message('Assistant'):
                st.markdown(assistant_message['content'])

    # Add any incomplete user message to the last expander
    if len(user_messages) > len(assistant_messages):
        with st.expander(f"Interaction {interaction_count + 1}", expanded=False):
            with st.chat_message('User'):
                st.markdown(user_messages[-1]['content'])


    # user input for chat
    if user_query := st.chat_input(f'Talk to {mascot}!', max_chars=4000):
        # Add user query to chat history
        state['chat_history'].append({
            'role': 'user', 
            'content': user_query
        })

        # Display user's message in the chat interface
        with st.chat_message('User'):
            st.markdown(user_query)

        # Generate assistant response
        with st.chat_message('Assistant'):
            truncated_chat_history = state['chat_history'][-CONTEXT_LIMIT:]
            messages = [
                HumanMessage(content=msg['content']) if msg['role'] == 'user' else AIMessage(content=msg['content'])
                for msg in truncated_chat_history
            ]
            full_response = st.write_stream(stream_llm_response(llm_stream, messages))

        # Add assistant response to chat history
        if full_response:
            state['chat_history'].append({
                'role': 'assistant', 
                'content': full_response
            })

        # Truncate the chat history to avoid excessive growth
        if len(state['chat_history']) > CONTEXT_LIMIT * 2:
            state['chat_history'] = state['chat_history'][-CONTEXT_LIMIT * 2:]

