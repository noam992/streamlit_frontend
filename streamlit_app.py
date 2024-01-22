import ast
import json
import logging
import os

import boto3
import pandas as pd
import streamlit as st
# from ..services.postgresql import get_rds_uri

# ***** CONFIGURABLE PARAMETERS *****
NO_ANSWER_MSG = "Sorry, I was unable to answer your question."
MODEL_NAME = os.environ.get("MODEL_NAME", "anthropic.claude-instant-v1")
LOGO_URL_1 = '<insert logo URL>'
LOGO_URL_2 = '<insert logo URL>'

def main():

    st.set_page_config(
        page_title="NLQ Demo",
        page_icon="🔎",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

        # store the initial value of widgets in session state
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False

    if "generated" not in st.session_state:
        st.session_state["generated"] = []

    if "past" not in st.session_state:
        st.session_state["past"] = []

    if "query" not in st.session_state:
        st.session_state["query"] = []

    if "query_text" not in st.session_state:
        st.session_state["query_text"] = []

    #Logos
    col1, col2 = st.columns(2)
    with col1:
        st.image(LOGO_URL_1, width=300)
    with col2:
        st.image(LOGO_URL_2, width=180)
                
    tab1, tab2, tab3 = st.tabs(["Chatbot", "Details", "Technologies"])

    with tab1:
        col1, col2 = st.columns([6, 1], gap="medium")

        with col1:
            with st.container():
                st.markdown("## OMOP Sample")
                st.markdown(
                    "#### Query the OMOP dataset using natural language."
                )
                st.markdown(" ")
                with st.expander("Click here for sample questions..."):
                    st.markdown(
                        """
                        - Simple
                            - How many rows are in the measurement table?
                            - What is the amount of patients diagnosed with code 410.0-410.9? 
                        - Moderate
                            - What is the amount of patients, aged 18 and above, diagnosed with code 410.0-410.9? 
                        - Complex
                            - what is the amount of patients, aged 18 and above, diagnosed with code 410.0-410.9 that in the same visit also underwent procedure code 36.01, 36.06, 36.07, 36.09, 00.66, 00.63?
                        - Unrelated to the Dataset
                            - Give me a recipe for chocolate cake.
                            - Who is current USA President?
                    """
                    )
                st.markdown(" ")
            with st.container():
                input_text = st.text_input(
                    "Ask a question:",
                    "",
                    key="query_text",
                    placeholder="Your question here...",
                    on_change=clear_text(),
                )
                logging.info(input_text)
                user_input = st.session_state["query"]

                # if user_input:
                #     with st.spinner(text="Thinking..."):
                #         st.session_state.past.append(user_input)
                #         try:
                #             logging.warning("Q1")
                #             logging.warning(user_input)
                #             logging.warning("Q2")
                #             output = sql_db_chain(user_input)
                #             st.session_state.generated.append(output)
                #             logging.info(st.session_state["query"])
                #             logging.info(st.session_state["generated"])
                #         except Exception as exc:
                #             st.session_state.generated.append(NO_ANSWER_MSG)
                #             logging.error(exc)

                # https://discuss.streamlit.io/t/streamlit-chat-avatars-not-working-on-cloud/46713/2
                if st.session_state["generated"]:
                    with col1:
                        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
                            if (i >= 0) and (
                                st.session_state["generated"][i] != NO_ANSWER_MSG
                            ):
                                with st.chat_message(
                                    "assistant",
                                    #avatar=f"{BASE_AVATAR_URL}/{ASSISTANT_ICON}",
                                    #avatar="app/static/flaticon-24px.png",
                                ):
                                    st.write(st.session_state["generated"][i]["result"])
                                with st.chat_message(
                                    "user",
                                    #avatar=f"{BASE_AVATAR_URL}/{USER_ICON}",
                                ):
                                    st.write(st.session_state["past"][i])
                            else:
                                with st.chat_message(
                                    "assistant",
                                    #avatar=f"{BASE_AVATAR_URL}/{ASSISTANT_ICON}",
                                    #avatar="app/static/flaticon-24px.png",
                                ):
                                    st.write(NO_ANSWER_MSG)
                                with st.chat_message(
                                    "user",
                                    #avatar=f"{BASE_AVATAR_URL}/{USER_ICON}",
                                ):
                                    st.write(st.session_state["past"][i])
        with col2:
            with st.container():
                st.button("clear chat", on_click=clear_session)
    with tab2:
        with st.container():
            st.markdown("### Details")
            st.markdown("Amazon Bedrock Model:")
            st.code(MODEL_NAME, language="text")

            position = len(st.session_state["generated"]) - 1
            if (position >= 0) and (
                st.session_state["generated"][position] != NO_ANSWER_MSG
            ):
                st.markdown("Question:")
                st.code(
                    st.session_state["generated"][position]["query"], language="text"
                )

                st.markdown("SQL Query:")
                st.code(
                    st.session_state["generated"][position]["intermediate_steps"][1],
                    language="sql",
                )

                st.markdown("Results:")
                st.code(
                    st.session_state["generated"][position]["intermediate_steps"][3],
                    language="python",
                )

                st.markdown("Answer:")
                st.code(
                    st.session_state["generated"][position]["result"], language="text"
                )

                data = ast.literal_eval(
                    st.session_state["generated"][position]["intermediate_steps"][3]
                )
                if len(data) > 0 and len(data[0]) > 1:
                    df = None
                    st.markdown("Pandas DataFrame:")
                    df = pd.DataFrame(data)
                    df
    with tab3:
        with st.container():
            st.markdown("### Technologies")
            st.markdown(" ")

            st.markdown("##### Natural Language Query (NLQ)")
            st.markdown(
                """
            [Natural language query (NLQ)](https://www.yellowfinbi.com/glossary/natural-language-query), according to Yellowfin, enables analytics users to ask questions of their data. It parses for keywords and generates relevant answers sourced from related databases, with results typically delivered as a report, chart or textual explanation that attempt to answer the query, and provide depth of understanding.
            """
            )
            st.markdown(" ")

            st.markdown("##### The OMOP Sample Datasets")
            st.markdown(
                """
            [OMOP Sample](https://kineret.health.gov.il/en/omop-model) contains data about over 2,000 patients. The datasets are available on GitHub in CSV format, encoded in UTF-8. The datasets are also available in JSON. The datasets are provided to the public domain using a [CC0 License](https://creativecommons.org/publicdomain/zero/1.0/).
            """
            )
            st.markdown(" ")

            st.markdown(" ")

            st.markdown("##### Amazon Bedrock")
            st.markdown(
                """
            [Amazon Bedrock](https://aws.amazon.com/bedrock/) is the easiest way to build and scale generative AI applications with foundation models (FMs).
            """
            )

            st.markdown("##### LangChain")
            st.markdown(
                """
            [LangChain](https://python.langchain.com/en/latest/index.html) is a framework for developing applications powered by language models. LangChain provides standard, extendable interfaces and external integrations.
            """
            )
            st.markdown(" ")

            st.markdown("##### Chroma")
            st.markdown(
                """
            [Chroma](https://www.trychroma.com/) is the open-source embedding database. Chroma makes it easy to build LLM apps by making knowledge, facts, and skills pluggable for LLMs.
            """
            )
            st.markdown(" ")

            st.markdown("##### Streamlit")
            st.markdown(
                """
            [Streamlit](https://streamlit.io/) is an open-source app framework for Machine Learning and Data Science teams. Streamlit turns data scripts into shareable web apps in minutes. All in pure Python. No front-end experience required.
            """
            )

        with st.container():
            st.markdown("""---""")
            st.markdown(
                "![](app_src/assets/img/github-24px-blk.png) [Feature request or bug report?](https://github.com/aws-solutions-library-samples/guidance-for-natural-language-queries-of-relational-databases-on-aws/issues)"
            )
            #st.markdown(
            #    "![](app/static/github-24px-blk.png) [The MoMA Collection datasets on GitHub](https://github.com/MuseumofModernArt/collection)"
            #)
            st.markdown(
                "![](app_src/assets/img/flaticon-24px.png) [Icons courtesy flaticon](https://www.flaticon.com)"
            )

def clear_text():
    st.session_state["query"] = st.session_state["query_text"]
    st.session_state["query_text"] = ""


def clear_session():
    for key in st.session_state.keys():
        del st.session_state[key]

if __name__ == "__main__":
    main()
