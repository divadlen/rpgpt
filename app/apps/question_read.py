import streamlit as st 
from streamlit import session_state as state
import json
import pandas as pd

from utils.text import (
    normalize_string, 
    infer_sector_rows,
    preprocess_data,
)
from utils.path_utils import get_file_path
from utils.json_utils import custom_json_decoder


def main():
    state['filtered_df'] = state.get('filtered_df', None)
    state['user_answers'] = state.get('user_answers', {})
    state['qa_cache'] = state.get('qa_cache', {})
    state['current_page'] = state.get('current_page', 0)

    st.write(state['ANTHROPIC_API_KEY'])

    with st.sidebar:
        with st.expander('Cache'):
            st.write(state['qa_cache'])


        with st.expander('Save/Load Q&A', expanded=True):
            t1, t2 = st.tabs(['Save', 'Load'])
            with t1:
                download_qa_json()
            with t2:
                load_qa_json()

    st.info('Load Q&A from sidebar or "Get Questions" tab')
    t1, t2, t3 = st.tabs(["View Questions", "Generate Answers", "Reset"])
    with t1:
        view_questions()
    with t2:
        generate_answers()
    with t3:
        reset_answers()








def view_questions():
    if state['filtered_df'] is not None:
        total_questions = len(state['filtered_df'])
        questions_per_page = 10
        total_pages = (total_questions // questions_per_page) + (1 if total_questions % questions_per_page else 0)

        # get current questions to display based on current page
        start_idx = state['current_page'] * questions_per_page
        end_idx = start_idx + questions_per_page
        questions_to_display = state['filtered_df'].iloc[start_idx:end_idx]

        # Popover for Pagination Controls
        with st.popover("Page Navigation"):
            st.markdown("Navigate between pages and save your progress")

            # current page
            manual_page = st.number_input(
                "Current page",
                min_value=1,
                max_value=total_pages,
                value=state['current_page'] + 1,  # Starting value should be the current page + 1
                step=1,
                key="manual_page_input"
            )
            
            # When the page number is changed, update current_page and rerun
            if manual_page != state['current_page'] + 1:
                state['current_page'] = manual_page - 1
                st.rerun()
            
            c1, c2, c3 = st.columns([1, 6, 1])  # Empty column for alignment            
            with c1:
                if state['current_page'] > 0:
                    if st.button(':arrow_backward:', key='prev_page'):
                        state['current_page'] -= 1
                        st.rerun()
            
            with c3:
                if state['current_page'] < total_pages - 1:
                    if st.button(':arrow_forward:', key='next_page'):
                        state['current_page'] += 1
                        st.rerun()

        # display questions
        for idx, row in questions_to_display.iterrows():
            question_id = str(row['question_number'])
            question = row['2024_question']
            sector = row['sector']
            module_name = row['module_name']

            # Initialize each question entry if not already in qa_cache
            if question_id not in state['qa_cache']:
                state['qa_cache'][question_id] = {
                    'question': question,
                    'sector': sector,
                    'module_name': module_name,
                    'answer': ""  # Initialize with empty answer
                }
            # Load the existing answer if available, otherwise set to default
            answer = state['qa_cache'][question_id]['answer']

            with st.expander(f'**Question:** {question_id} | **Sector:** {sector}'):
                answer = st.text_area(
                    f'{question}',
                    value=answer,
                    key=f"answer_{question_id}",
                    max_chars=4000
                )
                state['qa_cache'][question_id]['answer'] = answer




def generate_answers():
    st.write('generate answers')
    pass





def reset_answers():
    reset_button = st.button('Reset Answers')
    if reset_button:
        for question_id, entry in state['qa_cache'].items():
            state['qa_cache'][question_id]['answer'] = ""

        st.success('Answers reset successfully')
        st.rerun()


def download_qa_json():
    # rerun first to get latest change
    qa_data = {
        'settings': {
            'sectors': state.get('settings', {}).get('sectors', []),
            'supply_chain': state.get('settings', {}).get('supply_chain', []),
            'ifrs_s2': state.get('settings', {}).get('ifrs_s2', []),
            'afi': state.get('settings', {}).get('afi', []),
            'module_name': state.get('settings', {}).get('module_name', []),
        },
        'qa': [
            {'question_id': question_id, 'question': entry['question'], 'answer': entry['answer']}
            for question_id, entry in state['qa_cache'].items()
        ]
    }
    
    # Preprocess the data to ensure it is JSON-safe
    qa_data['settings'] = preprocess_data(qa_data['settings'])
    qa_data['qa'] = [preprocess_data(entry) for entry in qa_data['qa']]
    
    st.download_button(
        label="Download Q/A as JSON",
        data=json.dumps(qa_data, indent=4),
        file_name="qa_data.json",
        mime="application/json",
    )



def load_qa_json():
    """Load Q&A data from a file."""
    with st.form("Load Q&A"):
        qa_file = st.file_uploader('Upload Q/A save file', accept_multiple_files=False, type=['json'])
        submit_button = st.form_submit_button("Load Q&A")
        
    if submit_button:
        if qa_file is not None:
            # Load the JSON data from the uploaded file
            qa_data = json.load(qa_file)
            
            # Extract settings and apply them to the state
            settings = qa_data.get('settings', {})
            state['settings'] = settings

            # Rebuild the filtered dataframe based on loaded settings
            qa_entries = qa_data.get('qa', [])
            state['qa_cache'] = {entry['question_id']: entry for entry in qa_entries}

            # Rebuild the filtered dataframe
            rebuild_filtered_df(settings)

            # Show success message and rerun
            st.success("Q&A data loaded successfully!")
            st.rerun()



def rebuild_filtered_df(settings):
    """Rebuild the filtered dataframe based on the loaded settings."""
    df = pd.read_csv(get_file_path('cdpq.csv'))
    df.columns = [normalize_string(col) for col in df.columns]
    sector_df = pd.read_csv(get_file_path('cdpq_sector_codes.csv'), header=0)
    sector_df.columns = [normalize_string(col) for col in sector_df.columns]

    # Reapply filters
    filtered_df = df[
        (df['supply_chain_only'].isin(settings.get('supply_chain', []))) 
        & (df['ifrs_s2'].isin(settings.get('ifrs_s2', []))) 
        & (df['afi'].isin(settings.get('afi', [])))
        & (df['module_name'].isin(settings.get('module_name', [])))
    ]

    if settings.get('sectors', []):
        selected_sector_codes = sector_df[sector_df['sector'].isin(settings['sectors'])]['sector_code'].tolist()
        filtered_df = infer_sector_rows(filtered_df, selected_sector_codes)

    state['filtered_df'] = filtered_df