import os

import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="LinguistFlow AI", layout="wide")

st.title("LinguistFlow AI: Adaptive Language Tutor")

# --- Interactive Polyglot Mode ---
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "streamlit"

def toggle_view():
    st.session_state.view_mode = "polyglot" if st.session_state.view_mode == "streamlit" else "streamlit"

st.sidebar.divider()
st.sidebar.subheader("Interface Mode")
if st.sidebar.button("🚀 Launch Polyglot Experience" if st.session_state.view_mode == "streamlit" else "🔙 Back to Classic Mode"):
    toggle_view()
    st.rerun()

if st.session_state.view_mode == "polyglot":
    with open("polyglot.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=900, scrolling=True)
    st.stop()

api_url = os.getenv("API_URL", "http://api:8000")


@st.cache_data(ttl=60)
def fetch_providers() -> dict:
    try:
        res = requests.get(f"{api_url}/api/v1/lessons/providers", timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.RequestException:
        try:
            res = requests.get(f"{api_url}/api/lesson/providers", timeout=5)
            res.raise_for_status()
            return res.json()
        except requests.RequestException:
            return {"defaultProvider": "ollama", "providers": {}}


providers_info = fetch_providers()
provider_map: dict[str, list[str]] = providers_info.get("providers", {})
default_provider = providers_info.get("defaultProvider", "ollama")

with st.sidebar:
    st.header("LLM Settings")
    st.caption(f"API: `{api_url}`")
    if not provider_map:
        st.warning("No LLM providers enabled. Set LLM_*_ENABLED=true and restart the API.")
        selected_provider = None
        selected_model = None
    else:
        provider_names = list(provider_map.keys())
        default_idx = (
            provider_names.index(default_provider) if default_provider in provider_names else 0
        )
        selected_provider = st.selectbox("Provider", provider_names, index=default_idx)
        models = provider_map.get(selected_provider, [])
        selected_model = st.selectbox("Model", models) if models else None
    if st.button("Refresh providers"):
        fetch_providers.clear()
        st.rerun()

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Dynamic Lesson")
    languages = [
        "English", "Japanese", "German", "Spanish", "Italian", "Korean",
        "Tupi-Guarani", "Norwegian", "French", "Belgian German", "Belgian French",
        "Portuguese", "Mandarin", "Russian", "Arabic"
    ]
    language = st.selectbox("I want to learn:", languages)
    topic = st.text_input("What topic?", "Ordering at a restaurant")
    hobby = st.text_input("My Hobby", "Football")
    student_id = st.text_input("Student ID", "STU123")

    if st.button("Generate Lesson"):
        if not selected_provider:
            st.error("Select an LLM provider first.")
        else:
            with st.spinner(f"AI is crafting your {language} lesson..."):
                payload = {
                    "studentId": student_id,
                    "topic": topic,
                    "hobby": hobby,
                    "language": language,
                    "provider": selected_provider,
                }
                if selected_model:
                    payload["model"] = selected_model
                try:
                    res = requests.post(f"{api_url}/api/v1/lessons", json=payload, timeout=180)
                    if res.status_code in (200, 201):
                        st.success("Lesson generated!")
                        data = res.json()
                        st.subheader(data.get("title", f"Lesson: {topic}"))
                        st.caption(f"Language: {data.get('target_language')} | Level: {data.get('difficulty_level')}")
                        if data.get("raw_content"):
                            st.markdown(data["raw_content"])
                        elif data.get("dialogue_script"):
                            st.markdown("### Dialogue Script")
                            for line in data["dialogue_script"]:
                                if isinstance(line, dict):
                                    speaker = line.get("speaker", "Tutor")
                                    text = line.get("text", "")
                                    translation = line.get("translation", "")
                                    st.write(f"**{speaker}:** {text}")
                                    if translation:
                                        st.caption(f"_{translation}_")
                        if data.get("cultural_tip"):
                            st.info(f"💡 Cultural Tip: {data['cultural_tip']}")
                    elif res.status_code == 429:
                        st.warning("Rate limit exceeded. Wait a moment and try again.")
                    elif res.status_code in (400, 422):
                        st.error(f"Invalid request: {res.text}")
                    elif res.status_code == 403:
                        st.error("Request blocked by security guardrails policy.")
                    else:
                        st.warning(f"API returned status {res.status_code}.")
                except requests.ConnectionError:
                    st.error("Could not connect to the API.")
                except requests.Timeout:
                    st.error("Request timed out. The API may be overloaded.")
                except requests.RequestException as e:
                    st.error(f"Request failed: {e}")

with col2:
    st.header("Pronunciation Lab")
    audio_file = st.file_uploader("Record your voice", type=["wav", "mp3", "ogg", "flac"])

    if audio_file:
        st.audio(audio_file)
        if st.button("Analyze Pronunciation"):
            with st.spinner("Analyzing wave patterns..."):
                try:
                    files = {"file": (audio_file.name, audio_file, audio_file.type)}
                    data = {"student_id": student_id}
                    res = requests.post(
                        f"{api_url}/api/speech/analyze",
                        files=files,
                        data=data,
                        timeout=120,
                    )
                    if res.status_code == 200:
                        analysis = res.json()
                        st.metric(
                            "Pronunciation Accuracy",
                            f"{int(analysis['pronunciation_score'] * 100)}%",
                            "+2%",
                        )
                        st.metric("Stress Level", analysis["stress_level"])
                        st.write(f"**Transcription:** {analysis['transcription']}")
                    elif res.status_code == 413:
                        st.error("Audio file is too large. Maximum size is 10 MB.")
                    elif res.status_code == 415:
                        st.error("Unsupported audio format. Use WAV, MP3, OGG or FLAC.")
                    elif res.status_code == 429:
                        st.warning("Rate limit exceeded. Wait a moment and try again.")
                    else:
                        st.error(f"API returned status {res.status_code}.")
                except requests.ConnectionError:
                    st.error("Could not connect to the API.")
                except requests.Timeout:
                    st.error("Analysis timed out.")
                except requests.RequestException as e:
                    st.error(f"Request failed: {e}")

st.divider()
st.header("Knowledge Heatmap (Graph Context)")
st.info("Connect to Neo4j to visualize your language knowledge graph.")
