import streamlit as st 
from streamlit import session_state as state
import pandas as pd

from utils.text import normalize_string

def main():
    state['filtered_df'] = state.get('filtered_df', None)
    state['user_answers'] = state.get('user_answers', {})
    state['qa_cache'] = state.get('qa_cache', {})
    state['current_page'] = state.get('current_page', 0)