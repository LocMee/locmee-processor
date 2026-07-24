import streamlit as st
import pandas as pd
import os
import re
import requests
from datetime import datetime
import noticias_locmee  # <--- 1. IMPORTANDO O NOVO MÓDULO

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="LocMee Data Processor", layout="wide")

# --- CSS CUSTOMIZADO PARA LAYOUT MOBILE PERFEITO ---
st.markdown("""
    <style>
    /* 1. Ocultar elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 2. Remover margens excessivas do topo para a caixa colar em cima */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    /* 3. Caixa de Título Centralizada e Ocupando Toda a Largura */
    .title-box {
        background-color: #f8f9fa;
        border-radius: 14px;
        padding: 18px 10px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        width: 100%;
    }

    /* 4. Fonte Maior e Ajustada para o Título */
    .title-box h3 {
        margin: 0 0 4px 0;
        color: #1e293b;
        font-size: 22px !important;
        font-weight: 700 !important;
    }

    /* 5. Subtítulo proporcional */
    .title-box p {
        margin: 0;
        color: #64748b;
        font-size: 13px !important;
    }

    /* 6. Espaçamentos gerais otimizados para toque no celular */
    .stSelectbox, .stTextInput, .stMarkdown {
        margin-bottom: 8px !important;
    }
    
    div[data-baseweb="select"] > div {
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Autenticação segura via Secrets do Streamlit
if "SENHA_ACESSO" in st.secrets:
    senha_correta = st.secrets["SENHA_ACESSO"]
else:
    senha_correta = "locmee2026"

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

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

# --- CABEÇALHO CUSTOMIZADO v4.18 (Centralizado e no Topo) ---
st.markdown("""
    <div class="title-box">
        <h3>📊 LocMee Data Processor</h3>
        <p>Consulta rápida e integrada ao repositório (v4.18)</p>
    </div>
""", unsafe_allow_html=True)

# --- FUNÇÃO PARA OBTER FERIADOS ---
@st.cache_data(ttl=86400)
def obter_calendario_nacional(ano, uf_filtro):
    feriados_lista = []
    try:
        url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            for f in response.json():
                feriados_lista.append({"date": f["date"], "name": f["name"], "tipo": "Nacional"})
    except Exception: pass
    return sorted(feriados_lista, key=lambda x: x["date"])

# Função para formatar o nome do responsável
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

    for col in df.columns:
        c_l = col.strip().lower()
        if c_l in ["nome do responsável", "nome do responsavel"] or "responsável" in c_l or "responsavel" in c_l:
            df[col] = df[col].apply(formatar_nome_responsavel)
    return df

def reorganizar_colunas(df, tipo_planilha):
    cols = list(df.columns)
    alvos = ["Atividade Turística", "Nome Fantasia", "Nome do Responsável", "E-mail Comercial", "Município", "UF"]
    novas_cols = [c for c in alvos if c in cols] + [c for c in cols if c not in alvos]
    return df[novas_cols]

# --- CRIAÇÃO DAS ABAS PRINCIPAIS ---
aba_consulta, aba_radar = st.tabs(["📊 Consultas de Bases", "🌐 Radar Global LocMee"])

with aba_consulta:
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

        # --- NOVO FILTRO DE UHs ESPECÍFICO PARA MEIOS DE HOSPEDAGEM ---
        faixa_uh = "Todos"
        if tipo_atual == "Meio de Hospedagem":
            st.markdown("---")
            faixa_uh = st.selectbox(
                "Filtrar por Número de UHs (Unidades Habitacionais):",
                [
                    "Todos",
                    "Até 20 UHs",
                    "De 21 a 50 UHs",
                    "De 51 a 100 UHs",
                    "De 101 a 200 UHs",
                    "Acima de 201 UHs"
                ],
                key="hosp_faixa_uh"
            )

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

        # Aplicação do filtro de UHs caso seja a aba de Hospedagem
        if tipo_atual == "Meio de Hospedagem" and faixa_uh != "Todos":
            col_uh_nome = None
            for c in df_filtrado_geo.columns:
                if c.strip().lower() in ["uhs", "uh", "quartos", "unidades habitacionais"]:
                    col_uh_nome = c
                    break
            
            if col_uh_nome:
                # Converte para numérico de forma segura para aplicar as faixas
                df_filtrado_geo[col_uh_nome] = pd.to_numeric(df_filtrado_geo[col_uh_nome], errors='coerce')
                if faixa_uh == "Até 20 UHs":
                    df_filtrado_geo = df_filtrado_geo[df_filtrado_geo[col_uh_nome] <= 20]
                elif faixa_uh == "De 21 a 50 UHs":
                    df_filtrado_geo = df_filtrado_geo[(df_filtrado_geo[col_uh_nome] >= 21) & (df_filtrado_geo[col_uh_nome] <= 50)]
                elif faixa_uh == "De 51 a 100 UHs":
                    df_filtrado_geo = df_filtrado_geo[(df_filtrado_geo[col_uh_nome] >= 51) & (df_filtrado_geo[col_uh_nome] <= 100)]
                elif faixa_uh == "De 101 a 200 UHs":
                    df_filtrado_geo = df_filtrado_geo[(df_filtrado_geo[col_uh_nome] >= 101) & (df_filtrado_geo[col_uh_nome] <= 200)]
                elif faixa_uh == "Acima de 201 UHs":
                    df_filtrado_geo = df_filtrado_geo[df_filtrado_geo[col_uh_nome] >= 201]
            else:
                st.warning("⚠️ Coluna de UHs / Quartos não encontrada nesta base para aplicar o filtro numérico.")

        with st.spinner(f"🔄 Higienizando {len(df_filtrado_geo)} registros..."):
            df = higienizar_base(df_filtrado_geo)
            df = reorganizar_colunas(df, tipo_atual)

        st.success(f"Base carregada e limpa: **{tipo_atual}** ({len(df)} registros válidos)")
        
        # --- OPÇÕES DE DOWNLOAD ---
        st.markdown("#### 📥 Opções de Download")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label=f"📥 Baixar Base Completa (.csv)",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"planilha_{tipo_atual.lower().replace(' ', '_')}_completa.csv",
                mime="text/csv"
            )
        with col_dl2:
            col_nome_mkt = col_email_mkt = None
            for c in df.columns:
                c_l = c.strip().lower()
                if c_l in ["nome do responsável", "nome do responsavel"] or "responsável" in c_l or "responsavel" in c_l:
                    col_nome_mkt = c
                    break
            if not col_nome_mkt:
                for c in df.columns:
                    if "nome" in c.lower() or "fantasia" in c.lower():
                        col_nome_mkt = c
                        break

            for c in df.columns:
                c_l = c.strip().lower()
                if c_l in ["e-mail comercial", "email comercial"] or ("e-mail" in c_l and "comercial" in c_l):
                    col_email_mkt = c
                    break

            if col_nome_mkt and col_email_mkt:
                df_mkt = df[[col_nome_mkt, col_email_mkt]].dropna(subset=[col_email_mkt])
                df_mkt = df_mkt[df_mkt[col_email_mkt].astype(str).str.strip() != ""]
                st.download_button(
                    label=f"🎯 Baixar Enxuta Marketing",
                    data=df_mkt.to_csv(index=False).encode('utf-8'),
                    file_name=f"marketing_{tipo_atual.lower().replace(' ', '_')}_enxuta.csv",
                    mime="text/csv",
                    type="primary"
                )
            else:
                st.warning("Colunas de marketing não localizadas.")

        # Bloco extra para cópia rápida de e-mails para marketing quando for Hospedagem ou geral
        if col_email_mkt and len(df) > 0:
            lista_emails_mkt = "; ".join(df[col_email_mkt].dropna().unique().tolist())
            if lista_emails_mkt:
                st.markdown("**📋 E-mails higienizados prontos para copiar e colar na sua campanha:**")
                st.text_area(
                    label="E-mails marketing separados por ponto e vírgula",
                    value=lista_emails_mkt,
                    height=90,
                    key="emails_copia_mkt"
                )

        st.markdown("---")
        
        # --- BUSCA E CONSULTA DE REGISTROS ---
        st.subheader("🔍 Consulta e Ficha de Cadastro")
        termo_busca = st.text_input("Digite o termo, Nome Fantasia, Responsável ou E-mail:")

        if termo_busca:
            with st.spinner("⏳ Buscando registro na base de dados..."):
                termo_limpo = termo_busca.strip()
                padrao_busca = rf'\b{re.escape(termo_limpo)}\b'
                mask_busca = df.astype(str).apply(
                    lambda row: row.str.contains(padrao_busca, case=False, na=False, regex=True)
                ).any(axis=1)
                df_busca = df[mask_busca]
            
            if len(df_busca) > 0:
                st.info(f"Encontrado(s) {len(df_busca)} registro(s) correspondente(s).")
                for idx, row in df_busca.head(10).iterrows():
                    def achar_valor(palavras_chave):
                        for col in df.columns:
                            if any(p in col.lower() for p in palavras_chave):
                                val = row[col]
                                if pd.notna(val): return str(val)
                        return "Não informado"

                    nome_fantasia = achar_valor(["nome fantasia", "razão social", "nome"])
                    certificado = achar_valor(["numero do certificado", "certificado", "cadastur"])
                    responsavel = achar_valor(["nome do responsável", "nome do responsavel", "responsável", "contato"])
                    telefone = achar_valor(["telefones", "telefone", "celular", "whatsapp", "fone"])
                    municipio = achar_valor(["município", "municipio", "cidade"])
                    uf = achar_valor(["uf", "estado", "sigla uf"])
                    
                    email_comercial = "Não informado"
                    for col in df.columns:
                        c_l = col.strip().lower()
                        if c_l in ["e-mail comercial", "email comercial"] or "e-mail" in c_l or "email" in c_l:
                            val = row[col]
                            if pd.notna(val) and str(val).strip() != "":
                                email_comercial = str(val)
                                break

                    ficha_texto = (
                        f"🏢 Nome: {nome_fantasia}\n"
                        f"📄 Inscrição Cadastur: {certificado}\n"
                        f"👤 Responsável: {responsavel}\n"
                        f"📍 Local: {municipio} - {uf}\n"
                        f"📞 Telefone: {telefone}\n"
                        f"📧 E-mail: {email_comercial}"
                    )

                    with st.container():
                        st.markdown(f"**Registro #{idx + 1}**")
                        st.text_area(label=f"Ficha - {nome_fantasia}", value=ficha_texto, height=145, key=f"ficha_{idx}")
                        st.markdown("---")
            else:
                st.warning("⚠️ Registro não localizado. Nenhum cadastro corresponde ao termo digitado.")
    else:
        st.error(f"⚠️ O arquivo correspondente (`{caminho_arquivo}`) ainda não foi encontrado na raiz do repositório.")

with aba_radar:
    # --- CHAMADA DO MÓDULO DE RADAR GLOBAL ---
    noticias_locmee.buscar_e_transformar_noticias()
