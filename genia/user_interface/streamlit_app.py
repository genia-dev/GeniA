import time
import uuid
import logging

import streamlit as st

from genia.agents.chat import OpenAIChat

oa = OpenAIChat()


class StreamlitApp:
    def __init__(self):
        st.title("Hello, Welcome to GeniA 🧬🤖💻 !")

        # Initialize chat conversation
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from conversation on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("What is up?"):
            # Add user message to chat conversation
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                if "session_id" not in st.session_state:
                    st.session_state["session_id"] = str(uuid.uuid4())

                logging.debug(f"session state: {st.session_state}")
                assistant_response = oa.process_message(prompt, st.session_state.session_id)
                # Simulate stream of response with milliseconds delay
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
