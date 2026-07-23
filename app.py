import streamlit as st
import pandas as pd
import os
import re
import requests
from datetime import datetime

# Configuração da página para aproveitar bem o espaço
st.set_page_config(page_title="LocMee Data Processor", layout="wide")

# --- OCULTAR ELEMENTOS PADRÃO DO STREAMLIT (MENU E FOOTER) PARA UX DE APP ---
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

    def password_entered():
        if st.session_state["password_input"] == senha_correta:
            st.session_state["password_correct"] = True
            st.session_state["password_input"] = ""
        else:
            st.session_state["password_correct"] = False

    st.text_input(
        "Digite a senha de acesso:",
        type="password",
        on_change=password_entered,
        key="password_input"
    )
    
    if "password_input" in st.session_state and not st.session_state["password_correct"] and st.session_state["password_input"] != "":
        st.error("Senha incorreta.")
        
    return st.session_state["password_correct"]

if not check_password():
    st.stop()

# --- CABEÇALHO PERSONALIZADO COM CAIXINHA ESTILIZADA (UX MELHORADA) ---
st.markdown("""
    <div style="padding: 15px 20px; background-color: #f8f9fa; border-radius: 12px; border: 1px solid #e9ecef; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #1e293b; font-size: 20px;">📊 LocMee Data Processor</h3>
        <p style="margin: 5px 0 0 0; color: #64748b; font-size: 13px;">Consulta rápida e integrada ao repositório (v4.16)</p>
    </div>
""", unsafe_allow_html=True)

# --- FUNÇÃO PARA OBTER FERIADOS NACIONAIS E ESTADUAIS DE TODAS AS UFS ---
@st.cache_data(ttl=86400)
def obter_calendario_nacional(ano, uf_filtro):
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
    except Exception:
        pass

    feriados_estaduais_brasil = {
        "AC": [{"date": f"{ano}-01-23", "name": "Fim da Revolução Acreana"}, {"date": f"{ano}-06-15", "name": "Aniversário do Acre"}],
        "AL": [{"date": f"{ano}-09-16", "name": "Emancipação Política de Alagoas"}, {"date": f"{ano}-11-20", "name": "Dia da Consciência Negra"}],
        "AP": [{"date": f"{ano}-03-19", "name": "Dia de São José"}, {"date": f"{ano}-09-13", "name": "Criação do Território Federal"}],
        "AM": [{"date": f"{ano}-09-05", "name": "Elevação do Amazonas à Província"}, {"date": f"{ano}-11-20", "name": "Dia da Consciência Negra"}],
        "BA": [{"date": f"{ano}-07-02", "name": "Independência da Bahia"}],
        "CE": [{"date": f"{ano}-03-19", "name": "Dia de São José"}, {"date": f"{ano}-03-25", "name": "Data Magna do Ceará (Fim da Escravidão)"}],
        "DF": [{"date": f"{ano}-04-21", "name": "Fundação de Brasília"}, {"date": f"{ano}-11-30", "name": "Dia do Evangélico"}],
        "ES": [{"date": f"{ano}-05-23", "name": "Colonização do Solo Espírito-Santense"}],
        "GO": [{"date": f"{ano}-07-26", "name": "Fundação da Cidade de Goiás"}],
        "MA": [{"date": f"{ano}-07-28", "name": "Adesão do Maranhão à Independência do Brasil"}],
        "MT": [{"date": f"{ano}-11-20", "name": "Dia da Consciência Negra"}],
        "MS": [{"date": f"{ano}-10-11", "name": "Criação do Estado de Mato Grosso do Sul"}],
        "MG": [{"date": f"{ano}-04-21", "name": "Data Magna de Minas Gerais (Tiradentes)"}],
        "PA": [{"date": f"{ano}-08-15", "name": "Adesão do Pará à Independência do Brasil"}],
        "PB": [{"date": f"{ano}-08-05", "name": "Fundação do Estado da Paraíba"}],
        "PR": [{"date": f"{ano}-12-19", "name": "Emancipação Política do Paraná"}],
        "PE": [{"date": f"{ano}-03-06", "name": "Revolução Pernambucana"}],
        "PI": [{"date": f"{ano}-10-19", "name": "Dia do Piauí"}],
        "RJ": [{"date": f"{ano}-04-23", "name": "Dia de São Jorge"}, {"date": f"{ano}-11-20", "name": "Dia da Consciência Negra"}],
        "RN": [{"date": f"{ano}-10-03", "name": "Mártires de Cunhaú e Uruaçu"}],
        "RS": [{"date": f"{ano}-09-20", "name": "Revolução Farroupilha (Data Magna)"}],
        "RO": [{"date": f"{ano}-01-04", "name": "Criação do Estado de Rondônia"}, {"date": f"{ano}-03-15", "name": "Criação do Território"}],
        "RR": [{"date": f"{ano}-10-05", "name": "Criação do Estado de Roraima"}],
        "SC": [{"date": f"{ano}-08-11", "name": "Criação da Província de Santa Catarina"}, {"date": f"{ano}-11-25", "name": "Dia de Santa Catarina de Alexandria"}],
        "SP": [{"date": f"{ano}-07-09", "name": "Revolução Constitucionalista de 1932"}, {"date": f"{ano}-11-20", "name": "Dia da Consciência Negra"}],
        "SE": [{"date": f"{ano}-07-08", "name": "Autonomia Política de Sergipe"}],
        "TO": [{"date": f"{ano}-03-18", "name": "Autonomia do Tocantins"}, {"date": f"{ano}-10-05", "name": "Criação do Estado"}]
    }

    if uf_filtro != "Todos" and uf_filtro in feriados_estaduais_brasil:
        for fe in feriados_estaduais_brasil[uf_filtro]:
            feriados_lista.append({
                "date": fe["date"],
                "name": f"{fe['name']} (Estadual - {uf_filtro})",
                "tipo": "Estadual"
            })
    elif uf_filtro == "Todos":
        for uf_sigla, lista_fes in feriados_estaduais_brasil.items():
            for fe in lista_fes:
                feriados_lista.append({
                    "date": fe["date"],
                    "name": f"{fe['name']} (Estadual - {uf_sigla})",
                    "tipo": "Estadual"
                })

    feriados_lista = sorted(feriados_lista, key=lambda x: x["date"])
    return feriados_lista

# Função para formatar o nome do responsável: retira preposições e mantém apenas os 2 primeiros nomes
def formatar_nome_responsavel(texto):
    if pd.isna(texto) or not isinstance(texto, str):
        return texto
    
    palavras_ignorar = {"de", "do", "da", "dos", "das", "e", "e."}
    
    tokens = texto.split()
    tokens_filtrados = [t for t in tokens if t.lower() not in palavras_ignorar]
    
    primeiros_dois = tokens_filtrados[:2]
    return " ".join(primeiros_dois)

# Função para higienizar e filtrar a base focando na coluna E-mail Comercial
def higienizar_base(df):
    col_alvo = None
    for col in df.columns:
        if col.strip().lower() == "e-mail comercial" or col.strip().lower() == "email comercial":
            col_alvo = col
            break
            
    if not col_alvo:
        for col in df.columns:
            if "e-mail" in col.lower() or "email" in col.lower():
                if "comercial" in col.lower():
                    col_alvo = col
                    break
    
    if not col_alvo:
        for col in df.columns:
            if "e-mail" in col.lower() or "email" in col.lower():
                col_alvo = col
                break
            
    if col_alvo:
        df[col_alvo] = df[col_alvo].astype(str)
        
        def extrair_primeiro_email(texto):
            if pd.isna(texto) or texto.lower() == 'nan':
                return ""
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', texto)
            if emails:
                return emails[0]
            return texto

        df[col_alvo] = df[col_alvo].apply(extrair_primeiro_email)

        # Filtrar cadastros de escritórios de contabilidade e afins
        termos_proibidos = [
            "contabil", "contabilidade", "escritorio", "escritório", 
            "fiscal", "dp", "rh", "financeiro", "adm", "administracao", 
            "assessor", "assessoria", "terceirizada", "counter"
        ]
        
        padrao_proibido = '|'.join(termos_proibidos)
        mask_proibido = df[col_alvo].str.contains(padrao_proibido, case=False, na=False)
        
        for col in df.columns:
            if any(t in col.lower() for t in ["nome", "fantasia", "razao"]):
                mask_proibido = mask_proibido | df[col].astype(str).str.contains(padrao_proibido, case=False, na=False)
                
        df = df[~mask_proibido].reset_index(drop=True)

    # Aplica a formatação específica na coluna de responsável (2 primeiros nomes sem preposições)
    for col in df.columns:
        c_l = col.strip().lower()
        if c_l in ["nome do responsável", "nome do responsavel"] or "responsável" in c_l or "responsavel" in c_l:
            df[col] = df[col].apply(formatar_nome_responsavel)

    return df

def reorganizar_colunas(df, tipo_planilha):
    cols = list(df.columns)
    
    if tipo_planilha == "Agências de Turismo":
        alvos = ["Atividade Turística", "Nome Fantasia", "Nome do Responsável", "E-mail Comercial", "Município", "UF"]
    elif tipo_planilha == "Guias de Turismo":
        alvos = ["Atividade Turística", "Nome do Responsável", "E-mail Comercial", "Município", "UF"]
    elif tipo_planilha == "Meio de Hospedagem":
        alvos = ["Atividade Turística", "Nome Fantasia", "Nome do Responsável", "E-mail Comercial", "Município", "UF"]
    elif tipo_planilha == "Locadora de Veículos":
        alvos = ["Atividade Turística", "Nome Fantasia", "Nome do Responsável", "E-mail Comercial", "Município", "UF"]
    else:
        alvos = ["Atividade Turística", "Nome Fantasia", "Nome do Responsável", "E-mail Comercial", "Município", "UF"]

    novas_cols = [c for c in alvos if c in cols] + [c for c in cols if c not in alvos]
    return df[novas_cols]

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

    # --- PRÉVIA DE 5 LINHAS COM ATIVIDADE TURÍSTICA E NOME FANTASIA ---
    st.markdown("### 📋 Prévia dos Dados Brutos (Primeiras 5 linhas)")
    cols_previa = []
    for c in df_raw.columns:
        c_l = c.strip().lower()
        if "atividade" in c_l or "turística" in c_l or "turistica" in c_l:
            cols_previa.append(c)
            break
    for c in df_raw.columns:
        c_l = c.strip().lower()
        if "nome fantasia" in c_l or "fantasia" in c_l:
            cols_previa.append(c)
            break
    
    if len(cols_previa) < 2 and len(df_raw.columns) >= 2:
        cols_previa = list(df_raw.columns[:2])

    st.dataframe(df_raw[cols_previa].head(5), use_container_width=True)
    st.markdown("---")

    # Identificar colunas de Estado e Município de forma flexível
    col_uf = None
    col_mun = None
    for c in df_raw.columns:
        c_l = c.strip().lower()
        if c_l in ["uf", "estado", "sigla uf"]:
            col_uf = c
        if c_l in ["município", "municipio", "cidade"]:
            col_mun = c

    # Filtros geográficos prévios
    st.markdown("### 📍 Filtro Geográfico Prévio")
    col_f1, col_f2 = st.columns(2)
    
    uf_selecionada = "Todos"
    mun_selecionado = "Todos"

    with col_f1:
        if col_uf:
            lista_ufs = ["Todos"] + sorted([str(x) for x in df_raw[col_uf].dropna().unique() if str(x).strip() != ""])
            uf_selecionada = st.selectbox("Filtrar por Estado (UF):", lista_ufs)
        else:
            st.info("Coluna de UF não localizada na planilha.")

    with col_f2:
        if col_mun:
            if col_uf and uf_selecionada != "Todos":
                df_mun_filtrado = df_raw[df_raw[col_uf].astype(str) == uf_selecionada]
            else:
                df_mun_filtrado = df_raw
            lista_muns = ["Todos"] + sorted([str(x) for x in df_mun_filtrado[col_mun].dropna().unique() if str(x).strip() != ""])
            mun_selecionado = st.selectbox("Filtrar por Município:", lista_muns)
        else:
            st.info("Coluna de Município não localizada na planilha.")

    # --- ALERTA DE FERIADOS NACIONAIS E ESTADUAIS DE TODAS AS UFS ---
    ano_atual = datetime.now().year
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    calendario = obter_calendario_nacional(ano_atual, uf_selecionada)

    feriado_hoje = next((f for f in calendario if f["date"] == data_hoje), None)

    if feriado_hoje:
        st.success(f"🎯 **Alerta de Feriado Hoje!** **{feriado_hoje['name']}**.")
    else:
        proximos = [f for f in calendario if f["date"] > data_hoje]
        if proximos:
            proximo = proximos[0]
            data_formatada = datetime.strptime(proximo["date"], "%Y-%m-%d").strftime("%d/%m/%Y")
            st.info(f"📅 **Próximo Feriado ({proximo['tipo']}):** **{proximo['name']}** em **{data_formatada}**.")

    # Aplicação dos filtros geográficos na base bruta
    df_filtrado_geo = df_raw.copy()
    if col_uf and uf_selecionada != "Todos":
        df_filtrado_geo = df_filtrado_geo[df_filtrado_geo[col_uf].astype(str) == uf_selecionada]
    if col_mun and mun_selecionado != "Todos":
        df_filtrado_geo = df_filtrado_geo[df_filtrado_geo[col_mun].astype(str) == mun_selecionado]

    st.markdown("---")

    with st.spinner(f"🔄 Higienizando registros filtrados..."):
        df = higienizar_base(df_filtrado_geo)
        df = reorganizar_colunas(df, tipo_atual)

    st.success(f"Base carregada e limpa com sucesso: **{tipo_atual}** ({len(df)} registros válidos após filtros)")
    
    # OPÇÕES DE DOWNLOAD NO TOPO
    st.markdown("### 📥 Opções de Download")
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        csv_completo = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Baixar Base Completa (.csv)",
            data=csv_completo,
            file_name=f"planilha_{tipo_atual.lower().replace(' ', '_')}_completa.csv",
            mime="text/csv"
        )
        
    with col_dl2:
        col_nome_mkt = None
        col_email_mkt = None
        
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
            if c_l == "e-mail comercial" or c_l == "email comercial" or ("e-mail" in c_l and "comercial" in c_l):
                col_email_mkt = c
                break

        if col_nome_mkt and col_email_mkt:
            df_mkt = df[[col_nome_mkt, col_email_mkt]].dropna(subset=[col_email_mkt])
            df_mkt = df_mkt[df_mkt[col_email_mkt].astype(str).str.strip() != ""]
            csv_mkt = df_mkt.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label=f"🎯 Baixar Enxuta Marketing (Responsável + E-mail)",
                data=csv_mkt,
                file_name=f"marketing_{tipo_atual.lower().replace(' ', '_')}_enxuta.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.warning("Colunas 'Nome do Responsável' ou 'E-mail Comercial' não localizadas para a versão enxuta.")

    st.markdown("---")
    
    st.subheader("🔍 Consulta e Ficha de Cadastro")
    st.markdown("Busque pelo nome, termo ou e-mail (ex: Aviva, Playcenter).")
    
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
            st.caption("💡 *Dica no celular: Toque na caixa abaixo para selecionar e copiar os dados para o WhatsApp.*")
            
            for idx, row in df_busca.head(10).iterrows():
                def achar_valor(palavras_chave):
                    for col in df.columns:
                        if any(p in col.lower() for p in palavras_chave):
                            val = row[col]
                            if pd.notna(val):
                                return str(val)
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
                    if c_l == "e-mail comercial" or c_l == "email comercial" or "e-mail" in c_l or "email" in c_l:
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
                    st.text_area(
                        label=f"Ficha - {nome_fantasia}",
                        value=ficha_texto,
                        height=145,
                        key=f"ficha_{idx}"
                    )
                    st.markdown("---")
        else:
            st.warning("⚠️ Registro não localizado. Nenhum cadastro corresponde ao termo digitado.")

else:
    st.error(f"⚠️ O arquivo correspondente (`{caminho_arquivo}`) ainda não foi encontrado na raiz do repositório.")
