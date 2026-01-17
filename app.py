import streamlit as st
from elevenlabs.client import ElevenLabs
import json

st.set_page_config(page_title="ComplianceScribe – PII Scanner", layout="wide")
st.title("ComplianceScribe")
st.markdown("**Enterprise tool prototype** using **ElevenLabs Scribe v2** – the most accurate STT model. Upload a customer support call → AI detects PII risks, labels speakers, timestamps words, and redacts sensitive info.")

# Sidebar for API key (secure input)
api_key = st.sidebar.text_input("ElevenLabs API Key", type="password", help="Get it from elevenlabs.io/account")
if not api_key:
    st.sidebar.info("Enter your API key to start.")
    st.stop()

client = ElevenLabs(api_key=api_key)

# File upload
uploaded_file = st.file_uploader("Upload call audio (mp3, wav, m4a, etc.)", type=["mp3", "wav", "m4a", "ogg"])

if uploaded_file:
    st.subheader(f"Processing: {uploaded_file.name}")
    
    with st.spinner("Transcribing + Analyzing with Scribe v2 (entity detection + diarization + word timestamps)..."):
        try:
            # Core Scribe v2 call – this enables ALL the good features!
            transcription = client.speech_to_text.transcribe(
                file=uploaded_file,
                model="scribe_v2",
                entity_detection=True,           # Detects PII, credit cards, names, health info, etc.
                diarization=True,                # Labels speakers (agent vs customer)
                word_level_timestamps=True       # Precise word start/end times
            )

            # Pull out the useful parts (based on docs response structure)
            full_text = transcription.text
            words = transcription.words if hasattr(transcription, 'words') else []  # word-level data
            entities = transcription.entities if hasattr(transcription, 'entities') else []  # PII entities

            st.success("Done! Scribe v2 analyzed the call.")

            # Layout: two columns for clean look
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Full Transcript")
                st.text_area("Raw Text", full_text, height=200)

            with col2:
                st.subheader("Redacted (Safe) Version")
                redacted = full_text
                for entity in entities:
                    redacted = redacted.replace(entity.text, f"[{entity.category}]")  # Simple replace
                st.text_area("PII Redacted", redacted, height=200)

            # PII Risks section
            st.subheader("Detected PII & Compliance Risks")
            if entities:
                for ent in entities:
                    st.markdown(f"- **{ent.category}**: '{ent.text}' (at ~{ent.start:.1f}s)")
            else:
                st.success("No PII risks found – compliant & safe!")

            # Speaker & Timestamps sample (shows technical depth)
            st.subheader("Speaker Diarization + Word Timestamps (Sample)")
            for w in words[:15]:  # Show first 15 words
                speaker = w.get('speaker_id', 'Unknown')
                st.write(f"Speaker {speaker}: '{w.text}' ({w.start:.1f}s – {w.end:.1f}s)")

            # Exports for pro feel
            st.download_button("Download Redacted TXT", redacted, "redacted_call.txt")
            st.download_button("Download Full Report JSON", json.dumps(transcription.to_dict(), indent=2), "compliance_report.json")

        except Exception as e:
            st.error(f"Oops: {str(e)}\nCommon fixes: Check API key, file size (< few minutes for free tier), or try shorter audio.")

st.markdown("**Why this wins**: Automates manual compliance review (costs companies $100k+/month). Built with Scribe v2's entity detection, diarization & word timestamps. #ScribeV2 contest entry.")
st.caption("Simple prototype by CUE | Deadline Jan 20, 2026")
