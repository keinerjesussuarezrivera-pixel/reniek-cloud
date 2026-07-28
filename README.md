# RENIEK Cloud

RENIEK Cloud no usa Ollama, Node.js, CMD ni tu PC como servidor. Gemini responde desde Google y Streamlit Cloud publica la aplicación para abrirla desde tablet, iPhone o computador.

## Archivos para GitHub

- `app.py`: aplicación de RENIEK estilo HUD/Jarvis.
- `requirements.txt`: únicas dependencias requeridas.
- `.streamlit/config.toml`: tema visual.
- `.streamlit/secrets.toml.example`: ejemplo de la clave. No subas un archivo real llamado `secrets.toml`.

## 1. Crear la API Key de Gemini

1. Entra a https://aistudio.google.com/app/apikey e inicia sesión con Google.
2. Pulsa **Create API key**.
3. Elige o crea un proyecto de Google.
4. Copia la clave y guárdala en un sitio privado. No la pegues en GitHub, imágenes ni mensajes públicos.

RENIEK usa Gemini 3.5 Flash, el modelo cloud actual configurado para responder con rapidez. Revisa los límites y condiciones de tu cuenta en Google AI Studio: la disponibilidad gratuita puede tener cuotas y cambiar según la cuenta o región.

## 2. Subir a GitHub

1. Crea un repositorio nuevo en https://github.com/new, por ejemplo `reniek-cloud`.
2. Sube **el contenido de esta carpeta**: `app.py`, `requirements.txt`, `.gitignore`, `README.md` y la carpeta `.streamlit`.
3. No subas `.streamlit/secrets.toml` ni ninguna clave.

## 3. Publicar en Streamlit Community Cloud

1. Entra a https://share.streamlit.io e inicia sesión con GitHub.
2. Pulsa **Create app** y selecciona tu repositorio `reniek-cloud`.
3. Selecciona la rama `main` y como archivo principal escribe `app.py`.
4. En **Advanced settings** > **Secrets**, pega exactamente:

```toml
GOOGLE_API_KEY = "TU_CLAVE_REAL_DE_GEMINI"
```

5. Pulsa **Deploy**.
6. Elige, si está disponible, el subdominio `reniek`; tu enlace final será similar a `https://reniek.streamlit.app`.

No necesitas ejecutar `streamlit run`, `ollama run` ni dejar tu PC encendido después de publicar.

## Seguridad

Una app pública permite que cualquiera que tenga el enlace haga consultas que consumen tu cuota de Gemini. No compartas la API Key y, si el enlace será público, controla a quién se lo envías.
