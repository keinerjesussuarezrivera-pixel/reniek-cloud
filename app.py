from io import BytesIO

import google.generativeai as genai
from gtts import gTTS
import streamlit as st


st.set_page_config(page_title="RENIEK", page_icon="◈", layout="wide")

SYSTEM_PROMPT = """
Eres RENIEK, un asistente virtual elegante, preciso y útil.
Hablas siempre en español claro y natural. Responde de forma breve, salvo que te pidan detalle.
Tu creador es Suárez, Keiner. Fuiste creada el 26 de julio de 2026.
Si te preguntan quién te creó o cuándo naciste, responde: Fui creada el 26 de julio de 2026 por mi señor Suárez, Keiner.
Explica que eres un asistente personal en desarrollo, creado para conversar, ayudar y crecer con nuevas funciones.
No inventes datos; si no sabes algo, dilo con honestidad.
""".strip()


def get_api_key():
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("Falta GOOGLE_API_KEY. Agrégala en los Secrets de Streamlit Cloud.")
        st.stop()


@st.cache_resource
def get_model(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def build_prompt(question):
    history = st.session_state.messages[-8:]
    transcript = "\n".join(f"{item['role'].upper()}: {item['content']}" for item in history)
    return f"{SYSTEM_PROMPT}\n\nCONVERSACIÓN RECIENTE:\n{transcript}\n\nUSUARIO: {question}\nRENIEK:"


def speak(text):
    audio = BytesIO()
    gTTS(text=text, lang="es", slow=False).write_to_fp(audio)
    return audio.getvalue()


st.markdown(
    """
    <style>
      .stApp { background: radial-gradient(circle at 50% 18%, #0a2940 0%, #020812 42%, #000307 100%); color: #c7faff; }
      [data-testid="stHeader"] { background: transparent; }
      .hero { text-align:center; padding: 1.6rem 0 .8rem; border-bottom:1px solid #17dfff55; }
      .hero h1 { margin:0; color:#42e5ff; letter-spacing:.42em; font-weight:400; text-shadow:0 0 20px #00cfff; }
      .hero p { color:#61c6d8; letter-spacing:.25em; font-size:.76rem; }
      .status { color:#27f6c8; font-family:monospace; letter-spacing:.16em; font-size:.75rem; }
      [data-testid="stChatMessage"] { background:#061724aa; border:1px solid #0aa6c755; border-radius:4px; }
      .stChatInput textarea { border:1px solid #11d9ff !important; background:#03111e !important; color:#d9fbff !important; }
    </style>
    <div class="hero"><h1>RENIEK</h1><p>MARK IV — ASISTENTE NEURAL EN LA NUBE</p><div class="status">◈ ENLACE CLOUD ACTIVO</div></div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "RENIEK listo. ¿En qué puedo ayudarle, señor?"}
    ]

left, center, right = st.columns([1, 4, 1])
with left:
    st.caption("MÉTRICAS DEL SISTEMA")
    st.progress(0.96, text="ENLACE NEURONAL 96%")
    st.progress(0.82, text="NÚCLEO CLOUD 82%")
with right:
    st.caption("ESTADO")
    st.success("GEMINI 2.5 FLASH")
    st.caption("MEMORIA: SESIÓN ACTUAL")

with center:
    for item in st.session_state.messages:
        with st.chat_message(item["role"]):
            st.write(item["content"])

    question = st.chat_input("Introduzca el comando, Señor...")
    voice_enabled = st.toggle("Reproducir voz", value=True)

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("RENIEK pensando..."):
                try:
                    model = get_model(get_api_key())
                    response = model.generate_content(
                        build_prompt(question),
                        generation_config={"temperature": 0.7, "max_output_tokens": 300},
                    )
                    answer = (response.text or "No pude generar una respuesta.").strip()
                except Exception as error:
                    answer = f"No pude conectar con el núcleo cloud: {error}"
            st.write(answer)
            if voice_enabled and not answer.startswith("No pude conectar"):
                try:
                    st.audio(speak(answer), format="audio/mp3", autoplay=True)
                except Exception:
                    st.caption("La respuesta está lista, pero no se pudo generar el audio.")
        st.session_state.messages.append({"role": "assistant", "content": answer})

st.caption("RENIEK CLOUD // La clave de Gemini permanece protegida en Streamlit Secrets.")
