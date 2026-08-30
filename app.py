import streamlit as st

from agent import answer_question


st.set_page_config(
    page_title="Skylark BI Agent",
    page_icon="🚁",
    layout="wide"
)


st.title("🚁 Skylark Drones BI Agent")

st.markdown(
    """
    Ask questions about **Deals** and **Work Orders**
    using live data from Monday.com.
    """
)


# Example questions

st.subheader("Try asking")

examples = [
    "What is our current pipeline?",
    "What are our top deals?",
    "How are our work orders doing?",
    "Which sectors have the most work orders?",
    "How much is receivable?",
    "Which sectors have strong pipeline but execution risk?"
]


cols = st.columns(3)

for i, question in enumerate(examples):

    if cols[i % 3].button(
        question,
        key=f"example_{i}"
    ):

        st.session_state["question"] = question


# Chat history

if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# User input

question = st.chat_input(
    "Ask a business question..."
)


if "question" in st.session_state:

    question = st.session_state.pop(
        "question"
    )


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    with st.chat_message("assistant"):

        with st.spinner(
            "Analyzing Monday.com data..."
        ):

            try:

                answer = answer_question(
                    question
                )

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                error_message = (
                    "I couldn't complete that analysis. "
                    f"Error: {str(e)}"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )


st.divider()

st.caption(
    "Data source: Monday.com • "
    "Results are generated from live board data."
)