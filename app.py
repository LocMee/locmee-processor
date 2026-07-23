import streamlit as st
import pandas as pd
import os
import re

# Configuração da página para aproveitar bem o espaço
st.set_page_config(page_title="LocMee Data Processor", layout="wide")

st.title("🔄 LocMee Data Processor (v4.5)")
st.markdown("Consulta rápida, organizada e integrada ao repositório para o trade turístico.")

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

# Função para remover preposições e conjunções dos nomes para o marketing
def limpar_preposicoes_nome(texto):
    if pd.isna(texto) or not isinstance(texto, str):
        return texto
    
    palavras_ignorar = {"de", "do", "da", "dos", "das", "e", "e."}
    
    tokens = texto.split()
    tokens_filtrados = [t for t in tokens if t.lower() not in palavras_ignorar]
    return " ".join(tokens_filtrados)

# Função para higienizar e filtrar a base focando na coluna E-mail Comercial
def higienizar_base(df):
    col_alvo = None
    for col in df.columns:
        col_limpa = col.strip().lower()
        if "e-mail" in col_limpa or "email" in col_limpa:
            if "comercial" in col_limpa:
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

    # Aplica a limpeza de preposições nas colunas de nome/responsável
    for col in df.columns:
        if any(t in col.lower() for t in ["nome", "fantasia", "razao", "responsável"]):
            df[col] = df[col].apply(limpar_preposicoes_nome)

    return df

def reorganizar_colunas(df, tipo_planilha):
    cols = list(df.columns)
    
    if tipo_planilha == "Agências de Turismo":
        alvos = ["Atividade Turística", "Nome Fantasia"]
    elif tipo_planilha == "Guias de Turismo":
        alvos = ["Atividade Turística", "Nome do Responsável"]
    elif tipo_planilha == "Meio de Hospedagem":
        alvos = ["Atividade Turística", "Nome Fantasia"]
    elif tipo_planilha == "Locadora de Veículos":
        alvos = ["Atividade Turística", "Nome Fantasia"]
    else:
        alvos = ["Atividade Turística", "Nome Fantasia"]

    novas_cols = [c for c in alvos if c in cols] + [c for c in cols if c not in cols]
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
    with st.spinner(f"🔄 Carregando e higienizando base de {tipo_atual}..."):
        df = pd.read_excel(caminho_arquivo)
        df = higienizar_base(df)
        df = reorganizar_colunas(df, tipo_atual)

    st.success(f"Base carregada e limpa com sucesso: **{tipo_atual}** ({len(df)} registros válidos)")
    
    # BOTÕES DE DOWNLOAD NO TOPO (COMPLETA + ENXUTA EXCLUSIVA PARA MARKETING)
    st.markdown("### 📥 Opções de Download")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_completo = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Baixar Base Completa (.csv)",
            data=csv_completo,
            file_name=f"planilha_{tipo_atual.lower().replace(' ', '_')}_completa.csv",
            mime="text/csv"
        )
        
    with col2:
        # Criar a base estritamente enxuta para marketing (apenas Nome e E-mail Comercial)
        col_nome_mkt = None
        for c in df.columns:
            if "nome" in c.lower() or "fantasia" in c.lower():
                col_nome_mkt = c
                break
                
        col_email_mkt = None
        for c in df.columns:
            if "e-mail" in c.lower() or "email" in c.lower():
                if "comercial" in c.lower():
                    col_email_mkt = c
                    break
        if not col_email_mkt:
            for c in df.columns:
                if "e-mail" in c.lower() or "email" in c.lower():
                    col_email_mkt = c
                    break

        if col_nome_mkt and col_email_mkt:
            df_mkt = df[[col_nome_mkt, col_email_mkt]].dropna(subset=[col_email_mkt])
            # Remove e-mails vazios ou "nan"
            df_mkt = df_mkt[df_mkt[col_email_mkt].astype(str).str.strip() != ""]
            csv_mkt = df_mkt.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label=f"🎯 Baixar Enxuta Marketing (Nome + E-mail)",
                data=csv_mkt,
                file_name=f"marketing_{tipo_atual.lower().replace(' ', '_')}_enxuta.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("Colunas de Nome ou E-mail não identificadas para o formato enxuto.")

    st.markdown("---")
    
    st.write("📋 **Pré-visualização (5 primeiras linhas):**")
    st.dataframe(df.head(5), use_container_width=True)
    if len(df) > 5:
        st.caption("Mostrando as primeiras 5 linhas na prévia.")

    st.markdown("---")
    
    st.subheader("🔍 Consulta e Ficha de Cadastro")
    st.markdown("Busque por parte do **Nome** ou do **Número do Certificado** para gerar o cartão de contato rápido.")
    
    termo_busca = st.text_input("Digite o Número do Certificado, Nome Fantasia ou Responsável:")

    if termo_busca:
        with st.spinner("⏳ Buscando registro na base de dados..."):
            df_busca = df[df.astype(str).apply(lambda row: row.str.contains(termo_busca, case=False, na=False)).any(axis=1)]
        
        if len(df_busca) > 0:
            st.info(f"Encontrado(s) {len(df_busca)} registro(s).")
            st.caption("💡 *Dica no celular: Toque na caixa abaixo para selecionar e copiar os dados para o WhatsApp.*")
            
            for idx, row in df_busca.head(10).iterrows():
                def achar_valor(palavras_chave):
                    for col in df.columns:
                        if any(p in col.lower() for p in palavras_chave):
                            val = row[col]
                            if pd.notna(val):
                                return str(val)
                    return "Não informado"

                nome_fantasia = achar_valor(["nome fantasia", "razão social", "responsável", "nome"])
                certificado = achar_valor(["numero do certificado", "certificado", "cadastur"])
                responsavel = achar_valor(["responsável", "contato", "sócio", "proprietário"])
                telefone = achar_valor(["telefones", "telefone", "celular", "whatsapp", "fone"])
                
                email_comercial = "Não informado"
                for col in df.columns:
                    if "e-mail" in col.lower() or "email" in col.lower():
                        val = row[col]
                        if pd.notna(val):
                            email_comercial = str(val)
                        break

                ficha_texto = (
                    f"🏢 Nome: {nome_fantasia}\n"
                    f"📄 Inscrição Cadastur: {certificado}\n"
                    f"👤 Responsável: {responsavel}\n"
                    f"📞 Telefone: {telefone}\n"
                    f"📧 E-mail: {email_comercial}"
                )

                with st.container():
                    st.markdown(f"**Registro #{idx + 1}**")
                    st.text_area(
                        label=f"Ficha - {nome_fantasia}",
                        value=ficha_texto,
                        height=130,
                        key=f"ficha_{idx}"
                    )
                    st.markdown("---")
        else:
            st.warning("Nenhum cadastro encontrado com este termo.")

else:
    st.error(f"⚠️ O arquivo correspondente (`{caminho_arquivo}`) ainda não foi encontrado na raiz do repositório.")
