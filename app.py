
import os
import requests
import streamlit as st

# ============================================================
# JURON — ASSISTENTE JURÍDICO BRASILEIRO
# ============================================================

st.set_page_config(
    page_title="JURON ⚖️",
    page_icon="⚖️",
    layout="wide"
)

# ============================================================
# CONFIGURAÇÃO SEGURA DA API GROQ
# ============================================================

try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    GROQ_API_KEY = ""

GROQ_API_KEY = GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")

MODEL = "openai/gpt-oss-120b"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ============================================================
# ESTILO VISUAL
# ============================================================

st.markdown("""
<style>
    :root {
        --bg: #000000;
        --text: #e0e0e0;
        --border: #222222;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    .stChatMessage {
        background: #0a0a0a;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 14px;
    }

    .stChatMessage[data-testid="chat-message-user"] {
        border-left: 5px solid #444444;
    }

    .stChatMessage[data-testid="chat-message-assistant"] {
        border-left: 5px solid #777777;
    }

    .stChatInput textarea {
        background: #111111 !important;
        color: var(--text) !important;
        border: 1px solid #333333 !important;
        border-radius: 8px;
    }

    .logo-container {
        text-align: center;
        margin: 100px 0 60px;
    }

    .title {
        font-size: clamp(2rem, 7vw, 7rem);
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        letter-spacing: 10px;
        text-transform: uppercase;
        text-shadow: 0 0 30px rgba(255,255,255,0.08);
    }

    .justice-emojis {
        font-size: clamp(1.5rem, 4vw, 5rem);
        color: rgba(255,255,255,0.4);
        margin: 0 12px;
        vertical-align: middle;
    }

    hr {
        border-color: #222222;
        margin: 40px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOGOTIPO
# ============================================================

st.markdown("""
<div class="logo-container">
    <h1 class="title">
        <span class="justice-emojis">⚖️ 📚</span>
        JURON
        <span class="justice-emojis">⚖️ 📚</span>
    </h1>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ============================================================
# INICIALIZAÇÃO DA CONVERSA
# ============================================================

MENSAGEM_INICIAL = {
    "role": "assistant",
    "content": (
        "Oi! Sou o JURON, seu assistente jurídico com foco "
        "no Direito Brasileiro.\n\n"
        "Descreva sua dúvida ou situação para começarmos.\n\n"
        "Posso ajudar a compreender leis, procedimentos, "
        "documentos e possíveis caminhos jurídicos.\n\n"
        "Sou uma IA: minhas respostas devem ser verificadas "
        "e não substituem a orientação de um advogado."
    )
}

if "messages" not in st.session_state:
    st.session_state.messages = [MENSAGEM_INICIAL.copy()]

# ============================================================
# ENVIO DA SOLICITAÇÃO À GROQ
# ============================================================

def chamar_juron(historico, imagem_anexada=False):
    if not GROQ_API_KEY or len(GROQ_API_KEY.strip()) < 20:
        return (
            "❌ A chave da API Groq não foi configurada.\n\n"
            "No Streamlit Cloud, acesse Settings → Secrets "
            "e configure GROQ_API_KEY."
        )

    system_prompt = """
Você é JURON, um assistente de inteligência artificial
especializado em informações jurídicas brasileiras.

OBJETIVOS:
- Responder em português brasileiro claro e natural.
- Ser analítico, preciso, organizado e objetivo.
- Ajudar a compreender legislação, contratos, direitos,
  procedimentos, documentos e questões jurídicas.
- Distinguir fatos fornecidos pelo usuário de hipóteses.
- Não inventar leis, artigos, decisões judiciais, precedentes,
  números de processos ou citações.
- Quando possível, identificar a norma pertinente e explicar
  sua aplicação, considerando eventuais alterações legislativas.
- Explicar incertezas, riscos, prazos e informações que faltam.
- Não garantir resultados judiciais nem substituir um profissional.

ESTRUTURA SUGERIDA PARA CASOS CONCRETOS:
1. Resumo da situação.
2. Análise jurídica e base legal.
3. Pontos de atenção e riscos.
4. Próximos passos possíveis.

Adapte a estrutura à pergunta. Para dúvidas simples, responda
diretamente, sem criar seções desnecessárias.

Se faltarem informações essenciais, faça perguntas objetivas.
Não afirme que consultou fontes oficiais se isso não ocorreu.

Finalize as análises jurídicas com:
"Esta é uma análise geral gerada por IA e não substitui
a orientação de advogado habilitado."
"""

    mensagens_api = [{"role": "system", "content": system_prompt}]

    # Copia o histórico para não alterar a conversa original.
    for mensagem in historico:
        mensagens_api.append({
            "role": mensagem["role"],
            "content": mensagem["content"]
        })

    if imagem_anexada:
        for mensagem in reversed(mensagens_api):
            if mensagem["role"] == "user":
                mensagem["content"] += (
                    "\n\nO usuário anexou uma imagem. "
                    "Esta versão do aplicativo não envia o conteúdo "
                    "visual ao modelo. Não afirme que examinou a imagem. "
                    "Peça ao usuário que descreva ou transcreva seu conteúdo."
                )
                break

    payload = {
        "model": MODEL,
        "messages": mensagens_api,
        "temperature": 0.7,
        "max_completion_tokens": 1100,
        "stream": False,
        "include_reasoning": False
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json"
    }

    try:
        resposta = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        if resposta.status_code == 401:
            return (
                "❌ Erro 401: a chave da API foi rejeitada. "
                "Revogue a chave exposta, gere outra e atualize "
                "o segredo GROQ_API_KEY no Streamlit Cloud."
            )

        if resposta.status_code == 429:
            return (
                "❌ A Groq informou que o limite de utilização foi "
                "atingido. Aguarde ou verifique os limites da sua conta."
            )

        if resposta.status_code == 404:
            return (
                "❌ Modelo ou endpoint não encontrado. "
                "Verifique se o modelo está disponível para sua conta."
            )

        if resposta.status_code >= 400:
            try:
                detalhe = resposta.json().get("error", {}).get(
                    "message", resposta.text
                )
            except (ValueError, AttributeError):
                detalhe = resposta.text

            return (
                f"❌ Erro da API Groq (HTTP {resposta.status_code}).\n\n"
                f"Detalhes: {str(detalhe)[:1000]}"
            )

        dados = resposta.json()
        escolhas = dados.get("choices", [])

        if not escolhas:
            return "❌ A API respondeu, mas não retornou uma resposta válida."

        conteudo = escolhas[0].get("message", {}).get("content")

        if not conteudo:
            return "❌ O modelo retornou uma resposta vazia. Tente novamente."

        return conteudo

    except requests.exceptions.Timeout:
        return (
            "⏳ A solicitação demorou demais para responder. "
            "Tente novamente."
        )

    except requests.exceptions.ConnectionError:
        return (
            "❌ Não foi possível conectar à API Groq. "
            "Verifique a conexão e tente novamente."
        )

    except requests.exceptions.RequestException as erro:
        return f"❌ Erro na comunicação com a API: {erro}"

    except (ValueError, KeyError, TypeError):
        return "❌ A resposta recebida da API não pôde ser interpretada."

# ============================================================
# ENVIO DE IMAGENS
# ============================================================

uploaded_file = st.file_uploader(
    "Envie uma imagem opcional (print, contrato ou e-mail)",
    type=["png", "jpg", "jpeg"]
)

imagem_anexada = uploaded_file is not None

if imagem_anexada:
    st.image(
        uploaded_file,
        caption="Imagem selecionada",
        width=400
    )
    st.info(
        "A imagem fica disponível para visualização nesta interface, "
        "mas seu conteúdo não é analisado pela IA nesta versão. "
        "Descreva ou transcreva o conteúdo na mensagem."
    )

# ============================================================
# EXIBIÇÃO DO HISTÓRICO
# ============================================================

for mensagem in st.session_state.messages:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

# ============================================================
# CHAT
# ============================================================

prompt = st.chat_input("Digite sua dúvida ou descreva seu caso jurídico...")

if prompt:
    conteudo_usuario = prompt

    if imagem_anexada:
        conteudo_usuario += (
            "\n\n[Imagem anexada à interface; "
            "o conteúdo visual não foi enviado à IA.]"
        )

    mensagem_usuario = {
        "role": "user",
        "content": conteudo_usuario
    }

    st.session_state.messages.append(mensagem_usuario)

    with st.chat_message("user"):
        st.markdown(prompt)

        if imagem_anexada:
            st.caption("Imagem anexada à interface.")

    with st.chat_message("assistant"):
        with st.spinner("JURON analisando sua solicitação..."):
            resposta = chamar_juron(
                st.session_state.messages,
                imagem_anexada=imagem_anexada
            )

        st.markdown(resposta)

    st.session_state.messages.append({
        "role": "assistant",
        "content": resposta
    })

# ============================================================
# BARRA LATERAL
# ============================================================

with st.sidebar:
    st.markdown("## ⚖️ JURON")
    st.caption("Assistente jurídico com IA")

    st.divider()

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = [MENSAGEM_INICIAL.copy()]
        st.rerun()

    st.divider()

    st.caption(
        "As respostas são informativas e podem conter erros. "
        "Confira a legislação vigente e procure orientação "
        "profissional para decisões jurídicas importantes."
    )
