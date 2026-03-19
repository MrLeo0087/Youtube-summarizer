__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
with st.spinner("Importing Library ..... ",show_time= True):
    from streamlit_player import st_player
    from translate import translate_document
    from TRANSCRIPT.transcript import transcript_generator
    from summary_generator import summary
    from note_generate import generate_note
    from CHAT.general import GeneralAssistant
    from CHAT.rag_chatbot import RAGAssistant
    from CHAT.website_search import SearchAssistant
    from TRANSCRIPT.llm_transcript_generate import llm_transcript

st.set_page_config("Youtube video summarizer",page_icon='📄')


# ----------- Session management ------------------

if 'page' not in st.session_state:
    st.session_state.page = "home"

if 'video_url' not in st.session_state:
    st.session_state.video_url = ""

if 'gemini_key' not in st.session_state:
    st.session_state.gemini_key = ""

if 'output_lang' not in st.session_state:
    st.session_state.output_lang = ""

if 'transcript' not in st.session_state:
    st.session_state.transcript = ""

if 'summary' not in st.session_state:
    st.session_state.summary = ""

if 'summary_complexity' not in st.session_state:
    st.session_state.summary_complexity = ""

if 'summary_lang' not in st.session_state:
    st.session_state.summary_lang = ""

if 'note' not in st.session_state:
    st.session_state.note = ""

if 'note_complexity' not in st.session_state:
    st.session_state.note_complexity = ""

if 'note_lang' not in st.session_state:
    st.session_state.note_lang = ""

if 'rag_history' not in st.session_state:
    st.session_state.rag_history = []


if 'general_history' not in st.session_state:
    st.session_state.general_history = []

if 'search_chat_history' not in st.session_state:
    st.session_state.search_chat_history = []

if 'chat_page' not in st.session_state:
    st.session_state.chat_page = "menu_chat"


if 'chat_transcript' not in st.session_state:
    st.session_state.chat_transcript = ""

if 'chat_lang' not in st.session_state:
    st.session_state.chat_lang = ""


# ------------ Utility Function ----------------
def translate_function(full_text,note_lang):
    LANG_CODE = {
            "English": "en",
            "Nepali": "ne",
            "Hindi": "hi"
        }
    sample = full_text[:200]
    devanagari_chars = sum(1 for c in sample if '\u0900' <= c <= '\u097F')
    transcript_lang = "hi" if devanagari_chars > 20 else "en"
    target_lang = LANG_CODE.get(note_lang, 'en')
    if transcript_lang == target_lang:
        print(f"⏭️ Skipping translation — already in {target_lang}")
        translate_note = full_text
    else:
        print(f"🔄 Translating {transcript_lang} → {target_lang}")
        translate_note = translate_document(full_text, target=target_lang)

    return translate_note





# ------------ Side Bar --------------
with st.sidebar:
    st.title("Setting ⚙️",text_alignment="center")
    st.divider()
    url = st.text_input('Video URL',placeholder='Paste youtube video link')
    if url:
        st.session_state.video_url = url
        with st.spinner('Finding Video ...',show_time=True):
            st_player(url,height=150)


    if st.button("Home",use_container_width=True):
        st.session_state.page = "home"

    if st.button("Summary",use_container_width=True):
        st.session_state.page = "summary"

    if st.button("Chat",use_container_width=True):
        st.session_state.page = "chat"

    if st.button("Note",use_container_width=True):
        st.session_state.page = "note"


if st.session_state.page == 'home':
    st.header("Youtube Video Summarizer 🧾")
    st.subheader("By Darshan - V2")

    llm_choice = st.selectbox("Select LLM",['Default (GEMINI)'])

    if llm_choice == 'Default (GEMINI)':
        col1,col2 = st.columns(2)
        with col1:
            # gemini_api = st.text_input('Gemini API',placeholder='Gemini API key',value=st.session_state.get('gemini_key'),help="Get gemini API from https://aistudio.google.com/api-keys")
            gemini_api = st.text_input('Gemini API',placeholder='Gemini API key',value=st.session_state.gemini_key,type="password",help="Get gemini API from https://aistudio.google.com/api-keys")
            if gemini_api:
                st.session_state.gemini_key = gemini_api

        with col2:
            output_language = st.selectbox("Choose Transcript Language",['English','Nepali', 'Hindi'],help="This is language of transcript you get")
            st.session_state.output_lang = output_language

        st.success("Choose output language correctly. Otherwise output will not very good ")
        st.divider()

        LANG_CODE = {
            "English": "en",
            "Nepali": "ne",
            "Hindi": "hi"
        }

        if not st.session_state.transcript:
            full_transcript = ""
            transcript_box = st.empty()
            
            with col1:
                if st.button("Get Transcript",use_container_width=True,type='primary'):
                    required = ['video_url', 'gemini_key', 'output_lang']
                    missing_key = [k for k in required if not st.session_state.get(k)]
                    if missing_key:
                        st.warning(f"Please provide: {', '.join(missing_key)}")

                    else:
                        with st.spinner("Generating Transcript..."):
                            result = transcript_generator(
                                st.session_state.get('video_url'),
                                st.session_state.get('gemini_key'),
                                st.session_state.get('output_lang')
                            )
                            for i in result:
                                full_transcript += i
                                transcript_box.markdown(
                                    full_transcript
                                )
            with col2:
                if st.button("Get Transcript from gemini",use_container_width=True,type='primary'):
                    required = ['video_url', 'gemini_key', 'output_lang']
                    missing_key = [k for k in required if not st.session_state.get(k)]
                    if missing_key:
                        st.warning(f"Please provide: {', '.join(missing_key)}")

                    else:
                        with st.spinner("Generating Transcript (It can take some minute)..."):
                            result = llm_transcript(
                                st.session_state.get('video_url'),
                                st.session_state.get('gemini_key'),
                                st.session_state.get('output_lang')
                            )
                            for i in result:
                                full_transcript += i
                                transcript_box.markdown(
                                    full_transcript
                                )


        
                sample = full_transcript[:200]
                devanagari_chars = sum(1 for c in sample if '\u0900' <= c <= '\u097F')
                transcript_lang = "hi" if devanagari_chars > 20 else "en"
                target_lang = LANG_CODE.get(st.session_state.get('output_lang'), 'en')
                if transcript_lang == target_lang:
                    print(f"⏭️ Skipping translation — already in {target_lang}")
                    final_transcript = full_transcript
                else:
                    print(f"🔄 Translating {transcript_lang} → {target_lang}")
                    with st.spinner("Translating..."):
                        final_transcript = translate_document(full_transcript, target=target_lang)
                st.session_state.transcript = final_transcript
                transcript_box.empty()

        if st.session_state.get('transcript'):
            st.text_area('Full Transcript',value=st.session_state.get('transcript'),height=400)


                    

        st.divider()
        with st.expander('More Info'):
            st.write("""
                I use \n
                     gemini-2.5-flash-lite for summary
                     gemini-2.5-flash for note 
                     models/gemini-3.1-flash-lite-preview for chat
                """)



elif st.session_state.page == 'summary':
        if not st.session_state.get("transcript"):
            st.warning("Transcript not found. Please go back and process a video.")
            st.stop()

        if not st.session_state.get("gemini_key"):
            st.warning("Gemini API key is missing.")
            st.stop()

        st.header("Summary of video")
        st.divider()
        

        col_1, col_2 = st.columns(2)

        with col_1:
            complexity = st.selectbox("Choose Complexity", ["Medium", "Easy", "Hard"])
        with col_2:
            summary_lang = st.selectbox("Choose Language", ["English", "Hindi", "Nepali"])
        
        

        complexity_changed = complexity != st.session_state.summary_complexity
        language_changed = summary_lang != st.session_state.summary_lang


        if st.button("Generate summary"):
            st.session_state.summary_complexity = complexity
            st.session_state.summary_lang = summary_lang

            if not st.session_state.summary or complexity_changed:     
                st.session_state.summary = ""  
                note_box = st.empty()
                full_summary = ""

                with st.spinner("Generating summary..."):
                    try:
                        for chunk in summary(
                            st.session_state.get("transcript"),
                            st.session_state.get("gemini_key"),
                            summary_lang,
                            complexity
                        ):
                            full_summary += chunk
                            note_box.markdown(
                                full_summary
                            )
                        st.session_state.summary = full_summary

                        st.divider()
             
                    except Exception as e:
                        st.error(f"Failed to generate summary: {str(e)}")
            

            elif st.session_state.summary and language_changed:
                note_box = st.empty()
                full_note = st.session_state.get('summary')
                with st.spinner("Translating summary .... ",show_time=True):
                    translate_note = translate_function(full_note,summary_lang)
                    
                st.session_state.summary = translate_note

                note_box.markdown(
                                st.session_state.summary
                            )
                

        elif st.session_state.get("summary"):
            if complexity_changed or language_changed:
                st.warning("Settings changed. Click Generate Summary to regenerate.")


            note_box = st.empty()
            note_box.markdown(
                            st.session_state.get("summary")
            )

        if st.session_state.get("summary"):
            col_r1, col_r2 = st.columns([3, 1])
            with col_r1:
                st.divider()
                st.download_button(
                    "⬇️ Download Summary",
                    st.session_state.summary,
                    file_name="summary.md"
                )
            with col_r2:
                st.divider()
                if st.button("🔄 Regenerate", help="Clear and regenerate summary"):
                    st.session_state.summary = ""
                    st.session_state.summary_complexity = ""  
                    st.session_state.summary_lang = ""      
                    st.rerun()       



elif st.session_state.page == 'note':
    if not st.session_state.get("transcript"):
        st.warning("Transcript not found. Please go back and process a video.")
        st.stop()

    if not st.session_state.get("gemini_key"):
        st.warning("gemini API key is missing.")
        st.stop()

    st.header("Note of video")
    st.divider()
    

    col_1, col_2 = st.columns(2)

    with col_1:
        complexity = st.selectbox("Choose Complexity", ["Medium", "Easy", "Hard"])
    with col_2:
        note_lang = st.selectbox("Choose Language", ["English", "Hindi", "Nepali"])


    complexity_changed = complexity != st.session_state.note_complexity
    language_changed = note_lang != st.session_state.note_lang

    if st.button("Generate Note"):
        st.session_state.note_complexity = complexity
        st.session_state.note_lang = note_lang
        LANG_CODE = {
            "English": "en",
            "Nepali": "ne",
            "Hindi": "hi"
        }
        if not st.session_state.note or complexity_changed:     
            st.session_state.note = ""  
            note_box = st.empty()
            full_note = ""

            with st.spinner("Generating Note..."):
                try:
                    for chunk in generate_note(
                        st.session_state.get("transcript"),
                        st.session_state.get("gemini_key"),
                        note_lang,
                        complexity
                    ):
                        full_note += chunk
                        note_box.markdown(
                            full_note
                        )
                    st.session_state.note = full_note

                    st.divider()

                except Exception as e:
                    st.error(f"Failed to generate note: {str(e)}")
        

        elif st.session_state.note or language_changed:
            note_box = st.empty()
            full_note = st.session_state.get('note')
            with st.spinner("Translating Note .... ",show_time=True):
                translate_note = translate_function(full_note,note_lang)
            st.session_state.note = translate_note

            note_box.markdown(
                            st.session_state.note
                        )
            


    elif st.session_state.get("note"):
        if complexity_changed or language_changed:
            st.warning("Settings changed. Click Generate Summary to regenerate.")


        note_box = st.empty()
        note_box.markdown(
                        st.session_state.get("note")
        )
        
        
    if st.session_state.get("note"):
        st.divider()
        st.download_button(
            "⬇️ Download Summary",
            st.session_state.note,
            file_name="summary.md"
        )
        



#-----------------------C           H                A            T -------------------------

elif st.session_state.page == "chat":
    LANG_CODE = {"English": "en", "Nepali": "ne", "Hindi": "hi"}

    # --- FIX: Only translate if we haven't done it yet ---
    if not st.session_state.chat_transcript:
        sample_transcript = st.session_state.transcript
        sample = sample_transcript[:200]
        devanagari_chars = sum(1 for c in sample if '\u0900' <= c <= '\u097F')
        transcript_lang = "hi" if devanagari_chars > 20 else "en"
        
        if transcript_lang == 'en':
            print(f"⏭️ Skipping translation — already in English")
            final_transcript = sample_transcript
        else:
            print(f"🔄 Translating {transcript_lang} → English")
            with st.spinner("Translating transcript into english..."):
                final_transcript = translate_document(sample_transcript, target='en')
    
    # Now the rest of your code uses st.session_state.chat_transcript safely
        st.session_state.chat_transcript = final_transcript

    if st.session_state.chat_page == 'menu_chat':
        st.header("L.I.G.H.T Chatbot")
        st.divider()
        st.divider()
        st.subheader("Select a Chat Mode")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Video Chat", use_container_width=True):
                st.session_state.chat_page = 'video_chat'
                st.warning("First message can take serval minute to response.")
                st.rerun()
        with col2:
            if st.button("Search Chat", use_container_width=True):
                st.session_state.chat_page = 'search_chat'
                st.success('Search Recent Data or information')
                st.rerun()
        with col3:
            if st.button("General Chat", use_container_width=True):
                st.session_state.chat_page = 'general_chat'
                st.success("Fun with LIGHT")
                st.rerun()

    else:

        col1, col2 = st.columns([2, 4])
        with col1:
            if st.button("⬅ Back to Menu"):
                st.session_state.chat_page = 'menu_chat'
                st.rerun()

   

        if st.session_state.chat_page == 'general_chat':
            with col2:
                st.subheader("General Chat Mode")

            @st.cache_resource
            def get_general(api_key):
                return GeneralAssistant(api_key=api_key)
            
            general_light = get_general(st.session_state.get('gemini_key'))

            for msg in st.session_state.general_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            
            if user_query := st.chat_input("Let's have fun!"):
                with st.chat_message('human'):
                    st.write(user_query)

                st.session_state.general_history.append({"role": "human", "content": user_query})
                    
                with st.chat_message('assistant'):
                    with st.spinner("Thinking ..... "):
                        result = general_light.get_response(user_query,st.session_state.general_history)
                        full_reply = st.write_stream(result)

                st.session_state.general_history.append({"role": "assistant", "content": full_reply})

                st.rerun()

                # --- VIDEO CHAT MODE ---
        elif st.session_state.chat_page == 'video_chat':
            if not st.session_state.chat_transcript:
                st.warning('Transcript Not found !')
                st.stop()

            if not st.session_state.gemini_key:
                st.warning('Gemini api key not found')
                st.stop
        
            with col2:
                st.subheader("Video Chat Mode")

            @st.cache_resource
            def get_rag(api_key):
                return RAGAssistant(api_key=api_key)
            
            rag_light = get_rag(st.session_state.get('gemini_key')) 

            for msg in st.session_state.rag_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if user_query := st.chat_input("Ask me anything related to video!"):
                with st.chat_message('human'):
                    st.markdown(user_query)
                
                st.session_state.rag_history.append({"role": "human", "content": user_query})

                with st.chat_message('assistant'):
                    with st.spinner("Retrieving Information....", show_time=True):
                        result = rag_light.get_response(
                            user_query, 
                            st.session_state.chat_transcript
                        )
                        full_reply = st.write_stream(result)

                st.session_state.rag_history.append({"role": "assistant", "content": full_reply})
                st.rerun()

        # --- SEARCH CHAT MODE ---
        elif st.session_state.chat_page == 'search_chat':
            with col2:
                st.subheader("Search Chat Mode")

            @st.cache_resource
            def get_search(api_key):
                return SearchAssistant(api_key=api_key)

            search_light = get_search(st.session_state.get('gemini_key'))

            for msg in st.session_state.search_chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if user_query := st.chat_input("Ask me anything!"):
                with st.chat_message('human'):
                    st.markdown(user_query)

                st.session_state.search_chat_history.append({"role": "human", "content": user_query})
                
                with st.chat_message('assistant'):
                    with st.spinner("Searching Intelligence..."):
                        result = search_light.get_response(user_query, st.session_state.search_chat_history)
                        full_reply = st.write_stream(result)

                st.session_state.search_chat_history.append({"role": "assistant", "content": full_reply})
                st.rerun()