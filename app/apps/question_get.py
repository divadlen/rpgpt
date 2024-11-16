import streamlit as st 
from streamlit import session_state as state
import pandas as pd
import numpy as np
import json

from utils.text import (
    normalize_string, 
    infer_sector_rows,
    preprocess_data,
)
from utils.path_utils import get_file_path


# load data as globals
df = pd.read_csv(get_file_path('cdpq.csv'))
df.columns = [normalize_string(col) for col in df.columns]
df = df.replace({np.nan: 'NaN'})  # Replace NaNs with "NaN" string in the dataframe
sector_df = pd.read_csv(get_file_path('cdpq_sector_codes.csv'), header=0)
sector_df.columns = [normalize_string(col) for col in sector_df.columns]



def main():
    state['settings'] = state.get('settings', {})
    state['filtered_df'] = state.get('filtered_df', None)
    state['user_answers'] = state.get('user_answers', {})
    state['qa_cache'] = state.get('qa_cache', {})
    state['current_page'] = state.get('current_page', 0)



    with st.sidebar:
        with st.expander('Settings'):
            st.write(state['settings'])

        with st.expander('Cache'):
            st.write(state['qa_cache'])

    t1, t2 = st.tabs(["Get Questions", "Load Settings"])
    with t1:
        get_question_form()
    with t2:
        load_get_question_settings()









#----
# Parts
#----


def get_question_form():
    # Load previous settings or initialize default
    current_settings = state.get('settings', {})
    
    # Normalize filter values
    sectors = current_settings.get('sectors', [])
    supply_chain_status = current_settings.get('supply_chain', df['supply_chain_only'].unique().tolist())
    ifrs_s2_status = current_settings.get('ifrs_s2', df['ifrs_s2'].unique().tolist())
    afi_status = current_settings.get('afi', df['afi'].unique().tolist())
    modules = current_settings.get('module_name', df['module_name'].unique().tolist())

    # Normalize the filter options and the current settings to strings
    supply_chain_options, supply_chain_status = normalize_filter_values(df, 'supply_chain_only', supply_chain_status)
    ifrs_s2_options, ifrs_s2_status = normalize_filter_values(df, 'ifrs_s2', ifrs_s2_status)
    afi_options, afi_status = normalize_filter_values(df, 'afi', afi_status)
    module_options, modules = normalize_filter_values(df, 'module_name', modules)

    # filter widgets
    sectors = st.multiselect('Select Sectors', sector_df['sector'].unique().tolist(), default=sectors)
    supply_chain_status = st.multiselect('Supply Chain Status', supply_chain_options, default=supply_chain_status)
    ifrs_s2_status = st.multiselect('IFRS S2 Status', ifrs_s2_options, default=ifrs_s2_status)
    afi_status = st.multiselect('AFI Status', afi_options, default=afi_status)
    modules = st.multiselect('Select Modules', module_options, default=modules)

    # Buttons for actions
    c1, c2, c3 = st.columns(3)
    with c1:
        apply_button = st.button('Apply Filter')
    with c2:
        reset_button = st.button('Reset Settings')
    with c3:
        download_settings_json()

    if reset_button:
        state['settings'] = {
            'sectors': [],
            'supply_chain': df['supply_chain_only'].unique().tolist(),
            'ifrs_s2': df['ifrs_s2'].unique().tolist(),
            'afi': df['afi'].unique().tolist(),
            'module_name': df['module_name'].unique().tolist(),
        }
        st.rerun()


    if apply_button:
        # Prepare settings
        settings = {
            'sectors': sectors,
            'supply_chain': supply_chain_status,
            'ifrs_s2': ifrs_s2_status,
            'afi': afi_status,
            'module_name': modules,
        }

        # Apply filters using the helper function
        filtered_df, new_cache = apply_filters(df, sector_df, settings)

        # Update global state
        state['filtered_df'] = filtered_df
        state['qa_cache'] = new_cache
        state['settings'] = settings
        st.rerun()




def load_get_question_settings():
    with st.form("Load Settings"):
        settings = st.file_uploader("Upload settings file", type=["json"])
        submit_button = st.form_submit_button("Load Settings")

    if submit_button:
        json_content = json.load(settings)
        state['settings'] = json_content
        
        # Apply filters using the helper function
        filtered_df, new_cache = apply_filters(df, sector_df, json_content)

        # Update global state
        state['filtered_df'] = filtered_df
        state['qa_cache'] = new_cache
        st.text_area("Settings loaded successfully", json_content)
        st.success("Settings loaded successfully")
        st.rerun()




def download_settings_json():
    settings = preprocess_data(state['settings'])
    st.download_button(
        label="Download settings as JSON",
        data=json.dumps(settings, indent=4),
        file_name="settings.json",
        mime="application/json",
    )













#---
# Helper functions
#---


def normalize_filter_values(df, column, default_values):
    """
    Ensure that the filter options and default values are consistent and only contain strings.
    Example:
    
    >>> normalize_filter_values(df, 'sector', [1, 2, np.nan])
    (['1', '2', 'NaN'], ['1', '2', 'NaN'])
    """
    options = df[column].unique().tolist()
    options = [str(val) if val is not np.nan else "NaN" for val in options]
    
    # Ensure default values are also converted to strings
    default_values = [str(val) if val is not np.nan else "NaN" for val in default_values]
    
    return options, default_values



def apply_filters(df, sector_df, settings):
    """
    Apply filters to the given dataframe based on the settings.
    Returns the filtered dataframe and the updated qa_cache.
    """
    sectors = settings.get('sectors', [])
    supply_chain_status = settings.get('supply_chain', df['supply_chain_only'].unique().tolist())
    ifrs_s2_status = settings.get('ifrs_s2', df['ifrs_s2'].unique().tolist())
    afi_status = settings.get('afi', df['afi'].unique().tolist())
    modules = settings.get('module_name', df['module_name'].unique().tolist())

    # Normalize the filter options
    supply_chain_options, supply_chain_status = normalize_filter_values(df, 'supply_chain_only', supply_chain_status)
    ifrs_s2_options, ifrs_s2_status = normalize_filter_values(df, 'ifrs_s2', ifrs_s2_status)
    afi_options, afi_status = normalize_filter_values(df, 'afi', afi_status)
    module_options, modules = normalize_filter_values(df, 'module_name', modules)

    # Filter data based on sector selection
    if sectors == []:
        filtered_df = df
    else:
        selected_sector_codes = sector_df[sector_df['sector'].isin(sectors)]['sector_code'].tolist()
        filtered_df = infer_sector_rows(df, selected_sector_codes)

    # Apply other filters based on selection
    filtered_df = filtered_df[
        (filtered_df['supply_chain_only'].isin(supply_chain_status)) 
        & (filtered_df['ifrs_s2'].isin(ifrs_s2_status)) 
        & (filtered_df['afi'].isin(afi_status))
        & (filtered_df['module_name'].isin(modules))
    ]

    # Update qa_cache based on the filtered data
    new_cache = {}
    for idx, row in filtered_df.iterrows():
        question_id = str(row['question_number'])
        question = row['2024_question']
        sector = row['sector']
        module_name = row['module_name']

        # Retain answer if question exists in previous cache
        if question_id in state['qa_cache']:
            answer = state['qa_cache'][question_id].get('answer', "")
        else:
            answer = ""  # Initialize with empty answer
        
        new_cache[question_id] = {
            'question': question,
            'sector': sector,
            'module_name': module_name,
            'answer': answer
        }

    return filtered_df, new_cache
