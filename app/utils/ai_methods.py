from streamlit import session_state as state


def stream_llm_response(llm_stream, messages):
    """Stream the response from the LLM."""
    response_message = ""

    for chunk in llm_stream.stream(messages):
        response_message += chunk.content
        yield chunk
