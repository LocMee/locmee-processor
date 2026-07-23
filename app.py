import streamlit as st
import pandas as pd
import os
import re
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA (Layout Wide para melhor uso do espaço no mobile) ---
st.set_page_config(page_title="LocMee Data Processor", layout="wide")

# --- CSS CUSTOMIZADO PARA MELHORAR A UX NO MOBILE ---
st.markdown("""
    <style>
    /* 1. Ocultar elementos padrão do Streamlit (Menu e Footer) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 2. Ajustar o container principal para remover a margem superior padrão */
    .main .block-container {
        padding-top: 1rem !important; /* Reduz drasticamente o espaço em branco no topo */
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* 3. Estilo da Caixa de Título Principal (Centralizada e Ajustada) */
    .title-box {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 20px 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }

    /* 4. Título Maior e Negrito (Ocupando mais área) */
    .title-box h3 {
        margin: 0 0 5px 0;
        color: #1e293b;
        font-size: 24px !important; /* Fonte ligeiramente maior */
        font-weight: 700 !important;
    }

    /* 5. Subtítulo com fonte ajustada */
    .title-box p {
        margin: 0;
        color: #64748b;
        font-size: 14px !important;
    }

    /* 6. Ajustar o espaçamento de todos os elementos (reduzir paddings verticais) */
    .stSelectbox, .stTextInput, .stDataFrame, .stMarkdown {
        margin-bottom: 10px !important;
    }
    
    /* 7. Ajustar o tamanho da fonte do selectbox para facilitar o toque */
    div[data-baseweb="select"] > div {
        font-size: 16px !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# Autenticação segura via Secrets do Streamlit
if "SENHA_ACESSO" in st.secrets:
    senha_correta = st.secrets["SENHA_ACESSO"]
else:
    senha_correta = "locmee2026"  # fallback de segurança

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Centralizar o input da senha para ficar mais elegante
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_pwd1, col_pwd2, col_pwd3 = st.columns([1,3,1])
    with col_pwd2:
        st.markdown("<h3 style='text-align: center;'>🔐 Autenticação</h3>", unsafe_allow_html=True)
        st.text_input(
            "Digite a senha de acesso:",
            type="password",
            on_change=password_entered,
            key="password_input"
        )
        
        if "password_input" in st.session_state and not st.session_state["password_correct"] and st.session_state["password_input"] != "":
            st.error("Senha incorreta.")
            
    return st.session_state["password_correct"]

def password_entered():
    if st.session_state["password_input"] == senha_correta:
        st.session_state["password_correct"] = True
        st.session_state["password_input"] = ""
    else:
        st.session_state["password_correct"] = False

if not check_password():
    st.stop()

# --- CABEÇALHO CUSTOMIZADO v4.17 (Caixa preenchendo a largura e fonte aumentada) ---
st.markdown("""
    <div class="title-box">
        <h3>📊 LocMee Data Processor</h3>
        <p>Consulta rápida e integrada ao repositório (v4.17)</p>
    </div>
""", unsafe_allow_html=True)

# --- FUNÇÃO PARA OBTER FERIADOS ---
@st.cache_data(ttl=86400)
def obter_calendario_nacional(ano, uf_filtro):
    # ... (A mesma função da versão anterior, sem alterações) ...
    feriados_lista = []
    try:
        url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            for f in response.json():
                feriados_lista.append({
                    "date": f["date"],
                    "name": f["name"],
                    "tipo": "Nacional"
                })
    except Exception: pass
    
    # Feriados estaduais (simplificado para brevidade)
    feriados_estaduais_brasil = {
        "BA": [{"date": f"{ano}-07-02", "name": "Independência da Bahia"}],
        # ... adicione outros se necessário ...
    }
    
    # Adiciona feriados estaduais conforme filtro
    if uf_filtro != "Todos" and uf_filtro in feriados_estaduais_brasil:
        for fe in feriados_estaduais_brasil[uf_filtro]:
             feriados_lista.append({"date": fe["date"], "name": f"{fe['name']} ({uf_filtro})", "tipo": "Estadual"})
             
    return sorted(feriados_lista, key=lambda x: x["date"])

# Função para formatar o nome do responsável: retira preposições e mantém apenas os 2 primeiros nomes
def formatar_nome_responsavel(texto):
    if pd.isna(texto) or not isinstance(texto, str): return texto
    palavras_ignorar = {"de", "do", "da", "dos", "das", "e", "e."}
    tokens = texto.split()
    tokens_filtrados = [t for t in tokens if t.lower() not in palavras_ignorar]
    return " ".join(tokens_filtrados[:2])

# Função para higienizar e filtrar a base
def higienizar_base(df):
    col_alvo = None
    for col in df.columns:
        if col.strip().lower() in ["e-mail comercial", "email comercial"]: col_alvo = col; break
    if not col_alvo:
        for col in df.columns:
            if "e-mail" in col.lower() and "comercial" in col.lower(): col_alvo = col; break
    
    if col_alvo:
        df[col_alvo] = df[col_alvo].astype(str)
        def extrair_primeiro_email(texto):
            if pd.isna(texto) or texto.lower() == 'nan': return ""
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', texto)
            if emails: return emails[0]
            return texto
        df[col_alvo] = df[col_alvo].apply(extrair_primeiro_email)
        termos_proibidos = ["contabil", "contabilidade", "escritorio", "escritório", "fiscal", "dp", "rh", "financeiro", "adm", "administracao", "assessor", "assessoria", "terceirizada", "counter"]
        padrao_proibido = '|'.join(termos_proibidos)
        mask_proibido = df[col_alvo].str.contains(padrao_proibido, case=False, na=False)
        for col in df.columns:
            if any(t in col.lower() for t in ["nome", "fantasia", "razao"]):
                mask_proibido = mask_proibido | df[col].astype(str).str.contains(padrao_proibido, case=False, na=False)
        df = df[~mask_proibido].reset_index(drop=True)

    # Aplica a formatação específica na coluna de responsável
    for col in df.columns:
        c_l = col.strip().lower()
        if c_l in ["nome do responsável", "nome do responsavel"] or "responsável" in c_l or "responsavel" in c_l:
            df[col] = df[col].apply(formatar_nome_responsavel)
    return df

def reorganizar_colunas(df, tipo_planilha):
    cols = list(df.columns)
    if tipo_planilha in ["Agências de Turismo", "Meio de Hospedagem", "Locadora de Veículos", "Parques e Outros"]:
        alvos = ["Atividade Turística", "Nome Fantasia", "Nome do Responsável", "E-mail Comercial", "Município", "UF"]
    elif tipo_planilha == "Guias de Turismo":
        alvos = ["Atividade Turística", "Nome do Responsável", "E-mail Comercial", "Município", "UF"]
    else:
        alvos = ["Atividade Turística", "Nome Fantasia", "Nome do Responsável", "E-mail Comercial", "Município", "UF"]
    novas_cols = [c for c in alvos if c in cols] + [c for c in cols if c not in alvos]
    return df[novas_cols]

# --- LÓGICA PRINCIPAL ---
opcoes_planilhas = {
    "Agências de Turismo": "agencias.xlsx",
    "Guias de Turismo": "guias.xlsx",
    "Meio de Hospedagem": "hospedagens.xlsx",
    "Locadora de Veículos": "locadoras.xlsx",
    "Parques e Outros": "parques.xlsx"
}

tipo_atual = st.selectbox("Selecione a base de dados que deseja consultar:", list(opcoes_planilhas.keys()))
caminho_arquivo = opcoes_planilhas[tipo_atual]

if os.path.exists(caminho_arquivo):
    with st.spinner(f"📂 Lendo dados brutos de {tipo_atual}..."):
        df_raw = pd.read_excel(caminho_arquivo)

    # --- PRÉVIA DOS DADOS BRUTOS ---
    st.markdown("#### 📋 Prévia (5 linhas)")
    cols_previa = []
    for c in df_raw.columns:
        c_l = c.strip().lower()
        if "atividade" in c_l and "turística" in c_l: cols_previa.append(c); break
    for c in df_raw.columns:
        c_l = c.strip().lower()
        if "nome fantasia" in c_l or "fantasia" in c_l: cols_previa.append(c); break
    if len(cols_previa) < 2 and len(df_raw.columns) >= 2: cols_previa = list(df_raw.columns[:2])
    st.dataframe(df_raw[cols_previa].head(5), use_container_width=True, height=212)

    # Identificar colunas de Estado e Município
    col_uf = col_mun = None
    for c in df_raw.columns:
        c_l = c.strip().lower()
        if c_l in ["uf", "estado", "sigla uf"]: col_uf = c
        if c_l in ["município", "municipio", "cidade"]: col_mun = c

    # Filtros geográficos prévios
    st.markdown("#### 📍 Filtro Geográfico Prévio")
    col_f1, col_f2 = st.columns(2)
    uf_selecionada = mun_selecionado = "Todos"

    with col_f1:
        if col_uf:
            lista_ufs = ["Todos"] + sorted([str(x) for x in df_raw[col_uf].dropna().unique() if str(x).strip() != ""])
            uf_selecionada = st.selectbox("Filtrar por Estado (UF):", lista_ufs, key="filtro_uf")
        else: st.info("Coluna UF não localizada.")
    with col_f2:
        if col_mun:
            if col_uf and uf_selecionada != "Todos": df_mun_filtrado = df_raw[df_raw[col_uf].astype(str) == uf_selecionada]
            else: df_mun_filtrado = df_raw
            lista_muns = ["Todos"] + sorted([str(x) for x in df_mun_filtrado[col_mun].dropna().unique() if str(x).strip() != ""])
            mun_selecionado = st.selectbox("Filtrar por Município:", lista_muns, key="filtro_mun")
        else: st.info("Coluna Município não localizada.")

    # --- ALERTA DE FERIADOS ---
    ano_atual = datetime.now().year
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    calendario = obter_calendario_nacional(ano_atual, uf_selecionada)
    feriado_hoje = next((f for f in calendario if f["date"] == data_hoje), None)
    if feriado_hoje: st.success(f"🎯 **Alerta de Feriado Hoje!** **{feriado_hoje['name']}**.")
    else:
        proximos = [f for f in calendario if f["date"] > data_hoje]
        if proximos:
            proximo = proximos[0]
            data_formatada = datetime.strptime(proximo["date"], "%Y-%m-%d").strftime("%d/%m/%Y")
            st.info(f"📅 **Próximo Feriado ({proximo['tipo']}):** **{proximo['name']}** em **{data_formatada}**.")

    # Aplicação dos filtros geográficos
    df_filtrado_geo = df_raw.copy()
    if col_uf and uf_selecionada != "Todos": df_filtrado_geo = df_filtrado_geo[df_filtrado_geo[col_uf].astype(str) == uf_selecionada]
    if col_mun and mun_selecionado != "Todos": df_filtrado_geo = df_filtrado_geo[df_filtrado_geo[col_mun].astype(str) == mun_selecionado]

    with st.spinner(f"🔄 Higienizando {len(df_filtrado_geo)} registros..."):
        df = higienizar_base(df_filtrado_geo)
        df = reorganizar_colunas(df, tipo_atual)

    st.success(f"Base carregada e limpa: **{tipo_atual}** ({len(df)} registros válidos)")
    
    # OPÇÕES DE DOWNLOAD
    st.markdown("#### 📥 Opções de Download")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(label=f"📥 Baixar Base Completa (.csv)", data=df.to_csv(index=False).encode('utf-8'), file_name=f"planilha_{tipo_atual.lower().replace(' ', '_')}_completa.csv", mime="text/csv")
    with col_dl2:
        col_nome_mkt = col_email_mkt = None
        for c in df.columns:
            c_l
