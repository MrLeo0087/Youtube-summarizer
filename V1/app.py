import streamlit as st
from caption_generator import transcript_generator


st.set_page_config(
    page_title="Youtube Video Summarizer",
    page_icon="📄")

# ------- SESSION ---------
if 'transcript' not in st.session_state:
    st.session_state.transcript = "" 

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'gemini_api' not in st.session_state:
    st.session_state.gemini_api = ""

if 'groq_api' not in st.session_state:
    st.session_state.groq_api = ""

if 'llm_type' not in st.session_state:
    st.session_state.llm_type = "DEFAULT"

if 'url' not in st.session_state:
    st.session_state.url = ""

if 'summary' not in st.session_state:
    st.session_state.summary = ""

if 'note' not in st.session_state:
    st.session_state.note = ""

if 'history' not in st.session_state:
    st.session_state.history = []


# ----- SIDEBAR -------
with st.sidebar:
    st.markdown("""
        <div>
        <h2 style="font-family: Verdana, Geneva, Tahoma, sans-serif;font-size: 28px;text-align: center;">
                    SETTING⚙️
                    </h2>         
        </div>  
    """,unsafe_allow_html=True)
    st.divider()
    URL = st.text_input("Video URL",placeholder="Paste your link here",key="URL")
    st.session_state.url = URL
    st.divider()

    # BUTTON
    if st.button("GET TRANSCRIPT",type='primary',use_container_width=True):
        if st.session_state.url:
            transcript = transcript_generator(URL)
            full = ""
            for i in transcript:
                full+=i
            st.session_state.transcript = full
    if st.button('HOME🏡',use_container_width=True):
        st.session_state.page = "home"
        
    if st.button('SUMMARY📝',use_container_width=True):
        st.session_state.page = "summary"

    if st.button('CHAT💬',use_container_width=True):
        st.session_state.page = "chat"

    if st.button('NOTE🗒️',use_container_width=True):
        st.session_state.page = "note"


if st.session_state.page == 'home':
    st.title("Youtube Video Summarizer")
    st.subheader("By Darshan")

    st.divider()


    model_type = st.selectbox('Select LLM',['DEFAULT'])

    if model_type == "DEFAULT":
        st.session_state.llm_type = "DEFAULT"

        gemini_input = st.text_input("API KEY (GEMINI)", type="password", value=st.session_state.gemini_api)
        if gemini_input:
            st.session_state.gemini_api = gemini_input

        groq_input = st.text_input("API KEY (GROQ)", type="password", value=st.session_state.groq_api)
        if groq_input:
            st.session_state.groq_api = groq_input

        if st.session_state.gemini_api and st.session_state.groq_api:
            st.success("""\n
                        Summarize Model -> meta-llama/llama-4-scout-17b-16e-instruct \n 
                        Chat Model -> gemini-3.1-flash-lite-preview \n
                        Note Model -> gemini-2.5-flash""")

    # if model_type == "GEMINI":
    #     st.session_state.llm_type = "GEMINI"
    #     st.text_input("API KEY (GEMINI)", type="password", key="gemini_api")
    #     if st.session_state.gemini_api:
    #         st.success("""\n
    #                 Summarize Model -> gemini-2.5-flash \n 
    #                 Chat Model -> gemini-2.5-flash-lite \n
    #                 Note Model -> gemini-2.5-flash""")
        
    # elif model_type == "GROQ":
    #     st.session_state.llm_type = "GROQ"
    #     st.text_input("API KEY (GROQ)", type="password", key="groq_api")
    #     if st.session_state.groq_api:
    #         st.success("""\n
    #                 Summarize Model -> llama-3.1-8b-instant \n 
    #                 Chat Model -> meta-llama/llama-4-maverick-17b-128e-instruct \n
    #                 Note Model -> meta-llama/llama-4-scout-17b-16e-instruct""")
            
    # elif model_type == 'OLLAMA (LOCAL)':
    #     st.success("""\n
    #                 Summarize Model -> qwen2.5:3b \n 
    #                 Chat Model -> Phi-4-Mini \n
    #                 Note Model -> Phi-4-Mini""")
    if st.session_state.transcript:
        st.text_area('Transcript',height=800,value=st.session_state.transcript)
        
    

        
if st.session_state.page == 'summary':
    st.title("📝 Video Summary")
    st.divider()

    if not st.session_state.transcript:
        st.warning("⚠️ No transcript found. Please go to the sidebar and click 'GET TRANSCRIPT' first.")
    
    elif not st.session_state.groq_api:
        st.warning("⚠️ Groq API Key is missing. Please enter it on the Home page.")

    else:
        with st.sidebar:
            st.text_area('Transcript',height=800,value=st.session_state.transcript)
        if not st.session_state.summary:
            with st.spinner("Llama is reading the transcript... please wait..."):
                try:
                    from model_choice.default import summary
                    result = summary(st.session_state.groq_api, st.session_state.transcript)
                    st.session_state.summary = result
                    st.success("Summary Generated!")
                except Exception as e:
                    st.error(f"Error generating summary: {e}")

        st.warning("Final Summary")
        st.markdown(st.session_state.summary) 

        with st.expander("Edit Summary"):
            st.text_area(
                'Edit the markdown below:', 
                height=400, 
                value=st.session_state.summary,
                key="summary_editor"
            )

        st.divider()

        if st.button("🔄 Regenerate Summary"):
            st.session_state.summary = ""
            st.rerun()



if st.session_state.page == 'chat':
    st.title("L.I.G.H.T Chatbot")
    st.divider()

    if not st.session_state.get('gemini_api'):
        st.error("GEMINI API Empty or wrong. check again from home page")
    elif not st.session_state.get('transcript'):
        st.error("Transcript not available. Generate transcript first")
    else:
        from chatbot.light import chat
        from RAG.rag import query as rag_query, BM25Retriever, chunking 
        @st.cache_resource
        def prepare_retriever(text):
            chunks = chunking(text)
            retriever = BM25Retriever(chunks)
            return chunks, retriever

        chunks, bm25 = prepare_retriever(st.session_state.transcript)

        for msg in st.session_state.history:
            with st.chat_message(msg['role']):
                st.markdown(msg['message'])


        user_input = st.chat_input("Ask me anything")
        
        if user_input:

            with st.chat_message('user'):
                st.markdown(user_input)
            st.session_state.history.append({'role': 'user', 'message': user_input})

            context = rag_query(st.session_state.transcript, chunks,user_input,bm25)
            
            result = chat(st.session_state.gemini_api, user_input, context)

            with st.chat_message('assistant'):
                st.markdown(result)
            st.session_state.history.append({'role': 'assistant', 'message': result})



if st.session_state.page == 'note':
    st.title("🗒️Note")
    st.divider()

    if not st.session_state.transcript:
        st.warning("⚠️ No transcript found. Please go to the sidebar and click 'GET TRANSCRIPT' first.")
    elif not st.session_state.gemini_api:
        st.warning("⚠️ No API or wrong API. Please check gemini api key again")
    
    else:
        with st.sidebar:
            st.text_area('Transcript',height=800,value=st.session_state.transcript)
        if not st.session_state.note:
            with st.spinner("Generating Note from Video ..... "):
                try:
                    from model_choice.default import note
                    response = note(st.session_state.gemini_api,st.session_state.transcript)
                    st.session_state.note = response
                    st.success("✅ Note Complete")

                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown(st.session_state.note)
        with st.expander("Edit Note"):
            st.text_area(
                "Edit the note",
                height=800,
                value=st.session_state.note,
                key='note_editor_widget'
                )
        st.divider()
        if st.button('Regenerate Note'):
            st.session_state.note = ""
            st.rerun()
                    

