import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import streamlit as st
from rag import answer_question

st.set_page_config(page_title="Healthcare Information Assistant",layout="wide")

st.title("Healthcare Information Assistant")

question=st.text_input("Ask a medical question")

if st.button("Ask"):

    if question.strip()=="":

        st.warning("Please enter a question.")

    else:

        with st.spinner("Searching medical knowledge base..."):

            answer,level,score,sources,docs,faithful=answer_question(question)

        st.subheader("Answer")
        st.write(answer)

        if not faithful:
            st.caption(" This answer could not be fully verified against the retrieved sources.")

        st.subheader("Confidence")

        if level=="N/A":
            st.write(level)
        else:
            st.write(f"{level} ({score}%)")

        st.subheader("Sources")

        if len(sources)==0:

            st.write("No sources found.")

        else:

            for source in sources:

                if source["source"]=="WHO":

                    st.markdown(f"**WHO** - {source['title']}")

                    if "url" in source:
                        st.caption(source["url"])

                else:

                    st.markdown(f"**MedQuAD** - {source['question']}")

        with st.expander("Retrieved Evidence"):

            for i,doc in enumerate(docs):

                st.markdown(f"### Document {i+1}")

                if doc.metadata["type"]=="qa":

                    st.write(f"**Question:** {doc.metadata['question']}")
                    st.write(f"**Answer:** {doc.metadata['answer']}")

                else:

                    st.write(f"**Title:** {doc.metadata['title']}")
                    st.write(doc.page_content[:800])

                st.divider()
