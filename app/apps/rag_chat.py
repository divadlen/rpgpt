import streamlit as st
from streamlit import session_state as state

import time
import random

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage
import chromadb.api

from utils.ai_methods import (
    stream_llm_response,
    upload_form_for_rag,
    load_doc_to_db,
    initialize_vector_db,
)

def main():
    if state['selected_model'] in [None, ""]:
        st.error('Please input your API key and select a model')
        return
    
    state['uploaded_files'] = state.get('uploaded_files', [])
    state['processed_files'] = state.get('processed_files', [])
    state['vector_db'] = state.get('vector_db', None)
    
    with st.sidebar:
        clear_uploads = st.button('Clear Uploads', type='primary')
        if clear_uploads:
            state['uploaded_files'] = []
            state['processed_files'] = []
            st.rerun()

        inspect_chroma()


    with st.expander('Uploaded Files', expanded=True):
        upload_form_for_rag()

    load_doc_to_db()



def inspect_chroma():
    if state['vector_db'] is not None:
        chroma_client = state['vector_db']._client
        collection_names = [col.name for col in chroma_client.list_collections()]
        
        for collection_name in collection_names:
            # Fetch collection details
            collection = chroma_client.get_collection(collection_name)
            documents = collection.get()  # Retrieves vectors and metadata
            num_vectors = len(documents['documents'])
            
            with st.expander(f"Inspect VDB: {collection_name} (Vectors: {num_vectors})", expanded=False):
                if num_vectors == 0:
                    st.write("No vectors in this collection.")

                else:
                    sample = min(5, num_vectors)
                    random_vectors = random.sample(range(num_vectors), sample)

                    for i, idx in enumerate(random_vectors):  # Limit to first 5 for brevity
                        st.divider()
                        st.write(f"Sample {i + 1}:")
                        st.code(documents['documents'][idx]) 
