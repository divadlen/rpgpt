import streamlit as st
from streamlit import session_state as state

import os
from time import time

from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PDFMinerLoader,
    TextLoader,
)
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings


from utils.globals import MAX_TOTAL_FILE_SIZE



def stream_llm_response(llm_stream, messages):
    """
    Stream the response from the LLM.
    :param llm_stream: LLM stream
        Example: ChatOpenAI(model="gpt-4o-mini", temperature=0.3, streaming=True)

    :param messages: Messages to stream
        Example: [{"role": "user", "content": "Hello!"}]
    """
    response_message = ""

    for chunk in llm_stream.stream(messages):
        response_message += chunk.content
        yield chunk


# Helper: File loader mapping
def get_loader(file_path, file_type, file_name):
    """
    Load the appropriate file loader based on the file type.
    :param file_path: Path to the file
        Example: "C:/Users/user/Desktop/file.pdf"
    :param file_type: File type
        Example: "application/pdf"
    :param file_name: File name
        Example: "file.pdf"

    """
    if file_type == "application/pdf":
        return PDFMinerLoader(file_path)
    elif file_name.endswith(".docx"):
        return Docx2txtLoader(file_path)
    elif file_type in ["text/plain", "text/markdown"]:
        return TextLoader(file_path)
    elif file_name.endswith(".csv"):
        return CSVLoader(file_path, encoding="utf-8")
    else:
        return None


def upload_form_for_rag():
    """
    Streamlit form for uploading files for RAG

    Uploaded files will be in session state
    """
    state['uploaded_files'] = state.get('uploaded_files', [])

    with st.form("Upload Files"):
        uploaded_files =st.file_uploader(
            "Upload Files",
            label_visibility="collapsed",
            type=['pdf', 'docx', 'csv', 'txt', 'md'],
            accept_multiple_files=True,
        )
        submit_button = st.form_submit_button("Upload Files")

        if submit_button and uploaded_files:
            total_size = sum(file.size for file in state['uploaded_files'])

            for file in uploaded_files:
                if file in state['uploaded_files']:
                    st.warning(f"File {file.name} already exists")
                    continue

                if total_size + file.size > MAX_TOTAL_FILE_SIZE:
                    st.error(f"Unable to add {file.name}. Total file size exceeds {MAX_TOTAL_FILE_SIZE / (1024 * 1024)} MB")
                    continue
                
                state['uploaded_files'].append(file)
                total_size += file.size
            


def load_doc_to_db():
    """
    From session state, load uploaded files as chunks, embed and index in vdb
    """
    state['uploaded_files'] = state.get('uploaded_files', [])
    state['processed_files'] = state.get('processed_files', [])
    if state['uploaded_files'] == []:
        return
    
    docs = []
    for file in state['uploaded_files']:
        if file.name in state['processed_files']:
            continue  # Skip already processed files

        try:
            # save file temporarily
            os.makedirs('uploads', exist_ok=True)
            file_path = os.path.join('uploads', file.name)
            with open(file_path, 'wb') as f:
                f.write(file.read())

            # load uploaded document from temp file
            loader = get_loader(file_path, file.type, file.name)
            if loader is None:
                st.warning(f"Unable to load {file.name}. Unsupported file type of {file.type}")
                continue

            # add to docs and state
            new_docs = loader.load()
            docs.extend(new_docs)

            # Mark file as processed
            state['processed_files'].append(file.name)
            st.toast(f"Loaded {file.name} to database")

        except Exception as e:
            st.error(f"Error loading {file.name}: {e}")
            print(f"Error loading {file.name}: {e}")
        
        finally:
            # remove temporary file
            os.remove(file_path)
    
    if docs:
        split_and_load_docs(docs)

        with st.expander('Loaded Documents', expanded=True):
            st.write(doc.metadata['source'] for doc in docs)


    





def initialize_vector_db(docs):
    """
    Initializes the vector database using Chroma.
    Chroma is non persistent, so we need to initialize it every time we run the app.

    docs: List[Document]
    """
    if state['OPENAI_API_KEY'] in [None, ""]:
        st.error("Please set your OpenAI API key in the settings tab.")
        return
    
    embedding = OpenAIEmbeddings(api_key=state['OPENAI_API_KEY'])
    vector_db = Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory=None,
        collection_name=f"{str(time()).replace('.', '')[:14]}_" + state['session_id'],
    )

    # We need to manage the number of collections that we have in memory, we will keep the last 20
    chroma_client = vector_db._client
    collection_names = sorted([collection.name for collection in chroma_client.list_collections()])
    print("Number of collections:", len(collection_names))
    while len(collection_names) > 20:
        chroma_client.delete_collection(collection_names[0])
        collection_names.pop(0)

    return vector_db



def split_and_load_docs(docs):
    """
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=5000,
        chunk_overlap=1000,
    )
    document_chunks = text_splitter.split_documents(docs)

    with st.expander('Loaded Documents', expanded=False):
        st.write(f"Total Document Chunks: {len(document_chunks)}")
        for i, chunk in enumerate(document_chunks[:5]):  # Display first 5 chunks
            st.divider()
            st.code(chunk.page_content)
            st.code(chunk.metadata)

    if state['vector_db'] == None:
        state.vector_db = initialize_vector_db(docs)
    else:
        state.vector_db.add_documents(document_chunks)

