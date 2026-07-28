from io import BytesIO
from html import escape

from google import genai
from google.genai import types
from gtts import gTTS
import streamlit as st


st.set_page_config(page_title="RENIEK", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

MODEL_NAME = "gemini-3.5-flash"
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
        st.error("Falta la clave de Gemini. Agrégala en Streamlit Cloud → Settings → Secrets.")
        st.stop()


@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)


def build_prompt(question):
    history = st.session_state.messages[-8:]
    transcript = "\n".join(f"{item['role'].upper()}: {item['content']}" for item in history)
    return f"{SYSTEM_PROMPT}\n\nCONVERSACIÓN RECIENTE:\n{transcript}\n\nUSUARIO: {question}\nRENIEK:"


def generate_reply(question):
    response = get_client(get_api_key()).models.generate_content(
        model=MODEL_NAME,
        contents=build_prompt(question),
        config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=300),
    )
    return (response.text or "No pude generar una respuesta.").strip()


def speak(text):
    audio = BytesIO()
    gTTS(text=text, lang="es", slow=False).write_to_fp(audio)
    return audio.getvalue()


st.markdown(
    """
    <style>
      #MainMenu, footer, [data-testid="stHeader"] { visibility: hidden; }
      .stApp { background:#01070d; color:#b9f8ff; font-family:Consolas, monospace; }
      .block-container { max-width: 1550px; padding: .45rem 1rem 1.8rem; }
      .ticker { color:#00cceb; border-bottom:1px solid #07536c; font-size:.65rem; letter-spacing:.19em; padding:0 0 .5rem; white-space:nowrap; overflow:hidden; }
      .hero { text-align:center; padding:.8rem 0 .3rem; }
      .hero h1 { margin:0; color:#49e9ff; letter-spacing:.42em; font-weight:400; font-size:3rem; text-shadow:0 0 20px #00cfff; }
      .hero p { margin:.25rem 0; color:#007e9d; letter-spacing:.31em; font-size:.67rem; }
      .hero .ready { color:#1eefff; font-size:.67rem; letter-spacing:.2em; }
      .hud { border:1px solid #064763; background:#020b14cc; padding:.8rem; min-height:32rem; }
      .hud-title { color:#00cdf0; font-size:.68rem; font-weight:700; letter-spacing:.13em; border-bottom:1px solid #064763; padding-bottom:.55rem; margin-bottom:.7rem; }
      .metric { color:#9ef7ff; font-size:.64rem; letter-spacing:.05em; margin:.85rem 0 .28rem; }
      .bar { height:5px; background:#073246; } .bar i { display:block; height:100%; background:#11dbfa; box-shadow:0 0 9px #00d8ff; }
      .quantum i { background:#d94cff; }
      .system-line { color:#00aeca; font-size:.62rem; letter-spacing:.05em; margin:.55rem 0; }
      .orb-zone { display:flex; justify-content:center; align-items:center; height:235px; }
      .orb-rings { width:190px; height:190px; display:grid; place-items:center; border:1px solid #053e57; border-radius:50%; box-shadow:0 0 0 20px #02213255, 0 0 0 42px #01172188, 0 0 36px #00bde555; }
      .orb { width:118px; height:118px; border-radius:50%; background:radial-gradient(circle at 34% 25%, #b9ffff 0%, #39ddf5 17%, #08acd0 54%, #003554 100%); box-shadow:0 0 26px #00dfff, inset -16px -14px 25px #001526; }
      .waiting { color:#0089a8; text-align:center; letter-spacing:.35em; font-size:.67rem; margin:.45rem 0 1rem; }
      .log { border-bottom:1px solid #063447; padding:.6rem 0; color:#9fefff; font-size:.71rem; line-height:1.45; }
      .log strong { color:#00e3ff; }
      div[data-testid="stTextInput"] input { background:#03111f !important; color:#d9fbff !important; border:1px solid #00c9f3 !important; border-radius:0 !important; font-family:Consolas, monospace !important; }
      div[data-testid="stForm"] { border:1px solid #007d9f; background:#03101c; padding:.8rem; box-shadow:0 0 15px #00a8d633; }
      div.stButton > button { width:100%; background:#032033; color:#54eeff; border:1px solid #00b9e5; border-radius:0; font-family:Consolas, monospace; }
      div.stButton > button:hover { color:white; border-color:#68f6ff; background:#074059; }
      .stCheckbox label { color:#7eeaf5 !important; font-size:.74rem; }
      .stAlert { background:#081926; border:1px solid #087a99; color:#bffaff; }
      @media(max-width:800px) { .hero h1 { font-size:2rem; letter-spacing:.25em; } .hud { min-height:auto; } }
    </style>
    <div class="ticker">SÍNTESIS DE VOZ LISTA // MATRIZ DE MEMORIA CARGADA // RENIEK MARK IV // NÚCLEO NEURAL ACTIVO // ENLACE CLOUD ESTABLE //</div>
    <div class="hero"><h1>RENIEK</h1><p>MARK IV — SISTEMA DE INTELIGENCIA NEURAL</p><div class="ready">◆ EN ESPERA</div></div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "RENIEK listo. ¿En qué puedo ayudarle, señor?"}]

left, center, right = st.columns([1.05, 4.7, 1.05], gap="small")

with left:
    st.markdown('<div class="hud"><div class="hud-title">MÉTRICAS DEL SISTEMA</div><div class="metric">⚡ ENLACE NEURONAL&nbsp;&nbsp; 97.6 %</div><div class="bar"><i style="width:94%"></i></div><div class="metric">▣ NÚCLEO DE MEMORIA&nbsp;&nbsp; 65.8 %</div><div class="bar"><i style="width:66%"></i></div><div class="metric">⌘ UNIDAD DE PROCESAMIENTO&nbsp;&nbsp;43.8 %</div><div class="bar"><i style="width:44%"></i></div><div class="metric">⌁ ENLACE CUÁNTICO&nbsp;&nbsp;99.8 %</div><div class="bar quantum"><i style="width:99%"></i></div><div class="system-line">TIEMPO DE ACTIVIDAD&nbsp; CLOUD</div><div class="system-line">TEMPERATURA CENTRAL&nbsp; 36.2 °C</div><div class="system-line">SEÑAL&nbsp; FUERTE</div><div class="system-line">MODELO&nbsp; GEMINI FLASH</div></div>', unsafe_allow_html=True)

with center:
    st.markdown('<div class="orb-zone"><div class="orb-rings"><div class="orb"></div></div></div><div class="waiting">ESPERANDO COMENTARIOS, SEÑOR...</div>', unsafe_allow_html=True)
    for item in st.session_state.messages[-8:]:
        label = "SEÑOR" if item["role"] == "user" else "RENIEK"
        st.markdown(f'<div class="log"><strong>[ {label} ]</strong><br>{escape(item["content"])}</div>', unsafe_allow_html=True)

    voice_enabled = st.toggle("SÍNTESIS DE VOZ", value=True)
    with st.form("command_form", clear_on_submit=True):
        question = st.text_input("", placeholder="Introduzca el comando, Señor...", label_visibility="collapsed")
        submitted = st.form_submit_button("ENVIAR")

    if submitted and question.strip():
        question = question.strip()
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("RENIEK procesando..."):
            try:
                answer = generate_reply(question)
            except Exception:
                answer = "El núcleo cloud no pudo responder en este momento. Revise la clave de Gemini y vuelva a intentarlo."
        st.session_state.messages.append({"role": "assistant", "content": answer})
        if voice_enabled and not answer.startswith("El núcleo cloud"):
            try:
                st.session_state.pending_audio = speak(answer)
            except Exception:
                st.caption("La respuesta está lista, pero no se pudo generar el audio.")
        st.rerun()

    if st.session_state.get("pending_audio"):
        st.audio(st.session_state.pop("pending_audio"), format="audio/mp3", autoplay=True)

with right:
    st.markdown('<div class="hud"><div class="hud-title">REGISTRO DE COMUNICACIONES</div><div class="system-line">[ RENIEK ]<br>En espera de sus instrucciones.</div><div class="system-line">[ SISTEMA ]<br>Cloud sincronizado.</div><div class="system-line">[ MEMORIA ]<br>Sesión activa.</div></div>', unsafe_allow_html=True)

st.markdown('<div class="ticker" style="margin-top:.8rem">RENIEK CLOUD // LA CLAVE DE GEMINI PERMANECE PROTEGIDA EN STREAMLIT SECRETS //</div>', unsafe_allow_html=True)
