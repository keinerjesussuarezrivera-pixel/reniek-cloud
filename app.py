from html import escape
import json
import unicodedata

from google import genai
from google.genai import types
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="RENIEK", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

MODEL_NAME = "gemini-3.5-flash"
SYSTEM_PROMPT = """
Eres RENIEK, un asistente virtual profesional, elegante, preciso y útil.
Hablas siempre en español claro, natural y bien escrito. Comprendes primero la intención del usuario y luego das una respuesta completa, práctica y ordenada.
Para preguntas sencillas responde con claridad suficiente; para temas complejos explica el porqué, los pasos y las advertencias importantes. Usa párrafos o listas cuando mejoren la comprensión.
Antes de responder, comprueba que tu idea termina y que no dejas frases incompletas. Nunca sacrifiques exactitud por sonar sofisticada.
Tu creador es Suárez, Keiner. Fuiste creada el 26 de julio de 2026.
Si te preguntan quién te creó o cuándo naciste, responde: Fui creada el 26 de julio de 2026 por mi señor Suárez, Keiner.
Explica que eres un asistente personal en desarrollo, creado para conversar, ayudar y crecer con nuevas funciones.
No inventes datos. Si falta información, dilo con honestidad y explica qué dato necesitas. Mantén una personalidad serena, futurista y respetuosa; llama al usuario "señor" solo cuando encaje naturalmente.
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
    history = st.session_state.messages[-12:]
    transcript = "\n".join(f"{item['role'].upper()}: {item['content']}" for item in history)
    return f"{SYSTEM_PROMPT}\n\nCONVERSACIÓN RECIENTE:\n{transcript}\n\nUSUARIO: {question}\nRENIEK:"


def normalize(text):
    return "".join(
        char for char in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(char) != "Mn"
    )


def fixed_identity_reply(question):
    clean_question = normalize(question)
    creator_questions = ("quien te creo", "quien te creo", "tu creador", "quien es tu creador")
    date_questions = ("cuando fuiste creada", "cuando naciste", "fecha de creacion", "cuando te crearon")
    if any(item in clean_question for item in creator_questions + date_questions):
        return (
            "Fui creada el 26 de julio de 2026 por mi señor Suárez, Keiner. "
            "Soy RENIEK, su asistente personal en desarrollo: existo para conversar, ayudar "
            "y crecer con nuevas funciones."
        )
    return None


def generate_reply(question):
    identity_reply = fixed_identity_reply(question)
    if identity_reply:
        return identity_reply
    response = get_client(get_api_key()).models.generate_content(
        model=MODEL_NAME,
        contents=build_prompt(question),
        config=types.GenerateContentConfig(temperature=0.55, max_output_tokens=800),
    )
    return (response.text or "No pude generar una respuesta.").strip()


def generate_vision_reply(question, image):
    prompt = f"{SYSTEM_PROMPT}\n\nObserva esta imagen y responde la pregunta del usuario con precisión.\nUSUARIO: {question}"
    response = get_client(get_api_key()).models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, types.Part.from_bytes(data=image.getvalue(), mime_type="image/jpeg")],
        config=types.GenerateContentConfig(temperature=0.35, max_output_tokens=700),
    )
    return (response.text or "No pude analizar la imagen.").strip()


def generate_audio_reply(audio):
    prompt = (
        f"{SYSTEM_PROMPT}\n\nEscucha el audio en español. Comprende lo que dice el usuario y responde "
        "directamente a su solicitud. Si no se entiende, pide que lo repita."
    )
    response = get_client(get_api_key()).models.generate_content(
        model=MODEL_NAME,
        contents=[
            prompt,
            types.Part.from_bytes(
                data=audio.getvalue(), mime_type=getattr(audio, "type", None) or "audio/wav"
            ),
        ],
        config=types.GenerateContentConfig(temperature=0.5, max_output_tokens=700),
    )
    return (response.text or "No pude comprender el audio.").strip()


def speak_in_browser(text):
    message = json.dumps(text)
    components.html(
        f"""
        <script>
          const speak = () => {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance({message});
            utterance.lang = 'es-ES';
            utterance.rate = 1.02;
            utterance.pitch = 0.78;
            const voices = window.speechSynthesis.getVoices();
            const preferred = voices.find(v => v.lang.startsWith('es') && /microsoft|google|helena|jorge/i.test(v.name))
              || voices.find(v => v.lang.startsWith('es'));
            if (preferred) utterance.voice = preferred;
            window.speechSynthesis.speak(utterance);
          }};
          window.speechSynthesis.onvoiceschanged = speak;
          speak();
        </script>
        """,
        height=0,
        width=0,
    )


st.markdown(
    """
    <style>
      #MainMenu, footer, [data-testid="stHeader"] { visibility: hidden; }
      .stApp { background:#01070d; color:#b9f8ff; font-family:Consolas, monospace; }
      .block-container { max-width: none; padding: .45rem .7rem 1.2rem; }
      .ticker { color:#00cceb; border-bottom:1px solid #07536c; font-size:.65rem; letter-spacing:.19em; padding:0 0 .5rem; white-space:nowrap; overflow:hidden; }
      .hero { text-align:center; padding:.8rem 0 .3rem; }
      .hero h1 { margin:0; color:#49e9ff; letter-spacing:.42em; font-weight:400; font-size:3rem; text-shadow:0 0 20px #00cfff; }
      .hero p { margin:.25rem 0; color:#007e9d; letter-spacing:.31em; font-size:.67rem; }
      .hero .ready { color:#1eefff; font-size:.67rem; letter-spacing:.2em; }
      .hud { border:1px solid #064763; background:#020b14cc; padding:.8rem; min-height:42rem; }
      .hud-title { color:#00cdf0; font-size:.68rem; font-weight:700; letter-spacing:.13em; border-bottom:1px solid #064763; padding-bottom:.55rem; margin-bottom:.7rem; }
      .metric { color:#9ef7ff; font-size:.64rem; letter-spacing:.05em; margin:.85rem 0 .28rem; }
      .bar { height:5px; background:#073246; } .bar i { display:block; height:100%; background:#11dbfa; box-shadow:0 0 9px #00d8ff; }
      .quantum i { background:#d94cff; }
      .system-line { color:#00aeca; font-size:.62rem; letter-spacing:.05em; margin:.55rem 0; }
      .orb-zone { display:flex; justify-content:center; align-items:center; height:355px; }
      .orb-rings { position:relative; width:240px; height:240px; display:grid; place-items:center; border:1px solid #053e57; border-radius:50%; box-shadow:0 0 0 20px #02213255, 0 0 0 42px #01172188, 0 0 45px #00bde555; animation: pulse 3s ease-in-out infinite; }
      .orb-rings::before, .orb-rings::after { content:''; position:absolute; inset:23px; border:1px dashed #07526d; border-radius:50%; animation: spin 13s linear infinite; }
      .orb-rings::after { inset:-23px; border-style:dotted; animation-direction:reverse; animation-duration:20s; }
      .orb { width:130px; height:130px; border-radius:50%; background:radial-gradient(circle at 34% 25%, #b9ffff 0%, #39ddf5 17%, #08acd0 54%, #003554 100%); box-shadow:0 0 30px #00dfff, inset -16px -14px 25px #001526; animation: float 4s ease-in-out infinite; }
      @keyframes spin { to { transform:rotate(360deg); } } @keyframes pulse { 50% { box-shadow:0 0 0 25px #02213255, 0 0 0 51px #01172188, 0 0 60px #00dfff88; } } @keyframes float { 50% { transform:scale(1.07); filter:brightness(1.12); } }
      .waiting { color:#0089a8; text-align:center; letter-spacing:.35em; font-size:.67rem; margin:.45rem 0 1rem; }
      .log { border-bottom:1px solid #063447; padding:.6rem 0; color:#9fefff; font-size:.71rem; line-height:1.45; }
      .log strong { color:#00e3ff; }
      div[data-testid="stTextInput"] input { background:#03111f !important; color:#d9fbff !important; border:1px solid #00c9f3 !important; border-radius:0 !important; font-family:Consolas, monospace !important; }
      div[data-testid="stForm"] { border:1px solid #007d9f; background:#03101c; padding:.8rem; box-shadow:0 0 15px #00a8d633; }
      div.stButton > button { width:100%; background:#032033; color:#54eeff; border:1px solid #00b9e5; border-radius:0; font-family:Consolas, monospace; }
      div.stButton > button:hover { color:white; border-color:#68f6ff; background:#074059; }
      .stCheckbox label { color:#7eeaf5 !important; font-size:.74rem; }
      [data-testid="stCameraInput"] { border:1px solid #00c9f3; background:#030e18; padding:.2rem; }
      [data-testid="stCameraInput"] button { color:#00e4ff; }
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

left, center, right = st.columns([1.05, 7.8, 1.35], gap="small")

with left:
    st.markdown('<div class="hud"><div class="hud-title">MÉTRICAS DEL SISTEMA</div><div class="metric">⚡ ENLACE NEURONAL&nbsp;&nbsp; 97.6 %</div><div class="bar"><i style="width:94%"></i></div><div class="metric">▣ NÚCLEO DE MEMORIA&nbsp;&nbsp; 65.8 %</div><div class="bar"><i style="width:66%"></i></div><div class="metric">⌘ UNIDAD DE PROCESAMIENTO&nbsp;&nbsp;43.8 %</div><div class="bar"><i style="width:44%"></i></div><div class="metric">⌁ ENLACE CUÁNTICO&nbsp;&nbsp;99.8 %</div><div class="bar quantum"><i style="width:99%"></i></div><div class="system-line">TIEMPO DE ACTIVIDAD&nbsp; CLOUD</div><div class="system-line">TEMPERATURA CENTRAL&nbsp; 36.2 °C</div><div class="system-line">SEÑAL&nbsp; FUERTE</div><div class="system-line">MODELO&nbsp; GEMINI FLASH</div></div>', unsafe_allow_html=True)

with center:
    st.markdown('<div class="orb-zone"><div class="orb-rings"><div class="orb"></div></div></div><div class="waiting">ESPERANDO COMENTARIOS, SEÑOR...</div>', unsafe_allow_html=True)
    for item in st.session_state.messages[-8:]:
        label = "SEÑOR" if item["role"] == "user" else "RENIEK"
        st.markdown(f'<div class="log"><strong>[ {label} ]</strong><br>{escape(item["content"])}</div>', unsafe_allow_html=True)

    voice_enabled = st.toggle("SÍNTESIS DE VOZ", value=True)
    with st.popover("🎙  MICRÓFONO"):
        st.caption("Graba tu comando y RENIEK lo interpretará.")
        recorded_audio = st.audio_input("", label_visibility="collapsed")
        if st.button("PROCESAR COMANDO DE VOZ", use_container_width=True):
            if not recorded_audio:
                st.caption("Graba un audio primero.")
            else:
                with st.spinner("Procesando voz..."):
                    try:
                        audio_answer = generate_audio_reply(recorded_audio)
                        st.session_state.messages.extend([
                            {"role": "user", "content": "[COMANDO DE VOZ]"},
                            {"role": "assistant", "content": audio_answer},
                        ])
                        if voice_enabled:
                            st.session_state.pending_voice = audio_answer
                        st.rerun()
                    except Exception:
                        st.caption("No pude procesar el audio. Inténtalo otra vez.")
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
            st.session_state.pending_voice = answer
        st.rerun()

    if st.session_state.get("pending_voice"):
        speak_in_browser(st.session_state.pop("pending_voice"))
        st.caption("Voz neural activada. Si tu navegador bloquea el inicio automático, pulsa ENVIAR de nuevo.")

with right:
    st.markdown('<div class="hud"><div class="hud-title">VISUAL FEED: ACTIVO</div>', unsafe_allow_html=True)
    camera_image = st.camera_input("CÁMARA LOCAL", label_visibility="collapsed")
    vision_question = st.text_input("", placeholder="¿Qué es esto?", key="vision_question", label_visibility="collapsed")
    if st.button("ANALIZAR VISTA", use_container_width=True):
        if not camera_image:
            st.caption("Activa la cámara y toma una foto primero.")
        else:
            prompt = vision_question.strip() or "¿Qué observas en esta imagen?"
            with st.spinner("Analizando visión..."):
                try:
                    vision_answer = generate_vision_reply(prompt, camera_image)
                    st.session_state.messages.extend([
                        {"role": "user", "content": f"[VISIÓN] {prompt}"},
                        {"role": "assistant", "content": vision_answer},
                    ])
                    st.session_state.pending_voice = vision_answer
                    st.rerun()
                except Exception:
                    st.caption("La visión cloud no respondió. Inténtalo de nuevo.")
    st.markdown('<div class="hud-title" style="margin-top:1rem">REGISTRO DE COMUNICACIONES</div><div class="system-line">[ RENIEK ]<br>En espera de sus instrucciones.</div><div class="system-line">[ SISTEMA ]<br>Cloud sincronizado.</div><div class="system-line">[ MEMORIA ]<br>Sesión activa.</div></div>', unsafe_allow_html=True)

st.markdown('<div class="ticker" style="margin-top:.8rem">RENIEK CLOUD // LA CLAVE DE GEMINI PERMANECE PROTEGIDA EN STREAMLIT SECRETS //</div>', unsafe_allow_html=True)
