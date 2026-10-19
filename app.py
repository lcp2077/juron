import streamlit as st
import requests
import base64

# ==================== CONFIGURAÇÕES ====================
st.set_page_config(page_title="JURON ⚖️", page_icon="⚖️", layout="wide")

# ==================== GROQ API KEY ====================
GROQ_API_KEY = "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"

# ==================== TEMA JURÍDICO ====================
st.markdown("""
<style>
    :root {
        --bg: #000000;
        --text: #e0e0e0;
        --accent: #ffffff;
        --border: #222222;
    }
    .stApp { background: var(--bg); color: var(--text); }
    .stChatMessage {
        background: #0a0a0a;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .stChatMessage.user { border-left: 5px solid #444444; }
    .stChatMessage.assistant { border-left: 5px solid #777777; }
    .stChatInput textarea {
        background: #111111 !important;
        color: var(--text) !important;
        border: 1px solid #333333 !important;
        border-radius: 8px;
    }
    .logo-container {
        text-align: center;
        margin: 140px 0 80px;
    }
    .title {
        font-size: 7rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        letter-spacing: 14px;
        text-transform: uppercase;
        text-shadow: 0 0 30px rgba(255,255,255,0.08);
    }
    .justice-emojis {
        font-size: 5rem;
        color: rgba(255,255,255,0.4);
        margin: 0 20px;
        vertical-align: middle;
    }
    hr { border-color: #222222; margin: 40px 0; }
</style>
""", unsafe_allow_html=True)

# Logo
st.markdown("""
<div class="logo-container">
  <h1 class="title">
    <span class="justice-emojis">⚖️ 📚</span>JURON<span class="justice-emojis">⚖️ 📚</span>
  </h1>
</div>
""", unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)

# Upload de imagem
uploaded_file = st.file_uploader("Envie imagem (opcional - print, contrato, email...)", type=["png", "jpg", "jpeg"])
image_base64 = None
if uploaded_file is not None:
    if uploaded_file.type.startswith("image/"):
        image_bytes = uploaded_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        st.image(image_bytes, caption="Imagem enviada", width=400)
        st.info("Nota: A IA não analisa imagens diretamente. Descreva o conteúdo.")
    else:
        st.warning("Apenas imagens (png/jpg).")

# ==================== FUNÇÃO DA API ====================
def chamar_juron(image_b64=None):
    api_key = GROQ_API_KEY.strip()
    
    if not api_key or len(api_key) < 20:
        return "❌ Chave da API não configurada corretamente."

    system_prompt = """Você é JURON, uma IA jurídica útil, direta e inteligente.
Especialista em Direito Brasileiro (todas as áreas).
Seja natural e conversacional. Responda em português brasileiro fluente.
Estrutura para análise de caso: 1. Resumo 2. Base legal 3. Riscos e próximos passos.
Finalize sempre com: "Esta é uma análise geral de IA. Não substitua advogado habilitado." """

    messages = [{"role": "system", "content": system_prompt}]
   
    for m in st.session_state.messages:
        messages.append({"role": m["role"], "content": m["content"]})
    if image_b64:
        messages[-1]["content"] += "\n\n[Imagem enviada. Peça descrição ao usuário.]"

    payload = {
        "model": "openai/gpt-oss-120b",          # ← Modelo atualizado (o antigo foi desativado)
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1100,
        "stream": False
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=40
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
   
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            return "❌ Erro 401: Chave da API inválida ou expirada. Gere uma nova chave em console.groq.com/keys"
        if resp.status_code == 404:
            return "❌ Erro 404: Modelo não encontrado. O modelo antigo foi desativado."
        if resp.status_code == 429:
            return "❌ Limite da API Groq atingido. Tente novamente mais tarde."
        return f"Erro na API ({resp.status_code}): {str(e)}"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"

# ==================== CHAT ====================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Oi! Sou o JURON. Pode mandar sua dúvida jurídica ou enviar uma imagem.\n\nLembrete: sou IA, não substituo advogado."
    }]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Sua dúvida ou caso..."):
    full_content = prompt
    if image_base64:
        full_content += "\n\n[Imagem enviada]"
    st.session_state.messages.append({"role": "user", "content": full_content})
   
    with st.chat_message("user"):
        st.markdown(prompt)
        if image_base64:
            st.image(uploaded_file, width=400)
    
    with st.chat_message("assistant"):
        with st.spinner("JURON analisando..."):
            resposta = chamar_juron(image_base64)
            st.markdown(resposta)
   
    st.session_state.messages.append({"role": "assistant", "content": resposta})

# Sidebar
with st.sidebar:
    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
