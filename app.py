import streamlit as st
import pandas as pd
import os
import re

# Configuração da página para aproveitar bem o espaço (ótimo para mobile)
st.set_page_config(page_title="LocMee Data Processor", layout="wide")

st.title("🔄 LocMee Data Processor (v4.2)")
st.markdown("Consulta rápida, organizada e integrada ao repositório para o trade turístico.")

# Autenticação simples via Secrets do Streamlit
if "SENHA_ACESSO" in st.secrets:
    senha_correta = st.secrets["SENHA_ACESSO"]
else:
    senha_correta = "locmee2026"  # fallback caso não esteja configurado

def check_password():
    def password_entered():
        if st.session_state["password"] == senha_correta:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Digite a senha de acesso:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Digite a senha de acesso:", type="password", on_change=password_entered, key="password")
        st.error("Senha incorreta.")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Função para higienizar e filtrar a base olhando estritamente para a coluna "E-mail Comercial"
def higienizar_base(df):
    # Localizar exatamente a coluna "E-mail Comercial" (ignorando maiúsculas/minúsculas ou espaços extras)
    col_alvo = None
    for col in df.columns:
        if col.strip().lower() == "e-mail comercial" or col.strip().lower() == "email comercial":
            col_alvo = col
            break
            
    if col_alvo:
        # Converter para string para tratar
        df[col_alvo] = df[col_alvo].astype(str)
        
        # Deixar apenas o primeiro e-mail se houver mais de um na mesma célula
        def extrair_primeiro_email(texto):
            if pd.isna(texto) or texto.lower() == 'nan':
                return ""
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', texto)
            if emails:
                return emails[0] # Retorna estritamente o primeiro
            return texto

        df[col_alvo] = df[col_alvo].apply(extrair_primeiro_email)

        # Filtrar e remover cadastros de escritórios de contabilidade e afins
        termos_proibidos = [
            "contabil", "contabilidade", "escritorio", "escritório", 
            "fiscal", "dp", "rh", "financeiro", "adm", "administracao", 
            "assessor", "assessoria", "terceirizada", "counter"
        ]
        
        padrao_proibido = '|'.join(termos_proibidos)
        
        # Verifica se o termo proibido está na coluna E-mail Comercial ou no Nome/Razão Social
        mask_proibido = df[col_alvo].str.contains(padrao_proibido, case=False, na=False)
        
        for col in df.columns:
            if any(t in col.lower() for t in ["nome", "fantasia", "razao"]):
                mask_proibido = mask_proibido | df[col].astype(str).str.contains(padrao_proibido, case=False, na=False)
                
        # Mantém apenas quem NÃO tem os termos proibidos
        df = df[~mask_proibido].reset_index(drop=True)

    return df

# Função para reorganizar as colunas principais no topo conforme o tipo de planilha
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

    novas_cols = [c for c in alvos if c in cols] + [c for c in cols if c not in alvos]
    return df[novas_cols]

# Mapeamento das opções do menu para os arquivos salvos na raiz do repositório
opcoes_planilhas = {
    "Agências de Turismo": "agencias.xlsx",
    "Guias de Turismo": "guias.xlsx",
    "Meio de Hospedagem": "hospedagens.xlsx",
    "Locadora de Veículos": "locadoras.xlsx",
    "Parques e Outros": "parques.xlsx"
}

# Menu de seleção direto na tela
tipo_atual = st.selectbox("Selecione a base de dados que deseja consultar:", list(opcoes_planilhas.keys()))
caminho_arquivo = opcoes_planilhas[tipo_atual]

# Carregamento automático direto do repositório do GitHub com higienização estrita
if os.path.exists(caminho_arquivo):
    with st.spinner(f"🔄 Carregando e higienizando base de {tipo_atual}..."):
        df = pd.read_excel(caminho_arquivo)
        df = higienizar_base(df)       # Aplica o filtro restrito à coluna "E-mail Comercial"
        df = reorganizar_colunas(df, tipo_atual)

    st.success(f"Base carregada e limpa com sucesso: **{tipo_atual}** ({len(df)} registros válidos)")
    
    # Pré-visualização com 5 linhas
    st.write("📋 **Pré-visualização (5 primeiras linhas):**")
    st.dataframe(df.head(5), use_container_width=True)
    if len(df) > 5:
        st.caption("Mostrando as primeiras 5 linhas na prévia.")

    st.markdown("---")
    
    # Seção de Busca Rápida e Ficha de Contato
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
                
                # Puxando explicitamente da coluna E-mail Comercial na ficha também
                email_comercial = "Não informado"
                for col in df.columns:
                    if col.strip().lower() in ["e-mail comercial", "email comercial"]:
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

    # Botão de Download da Planilha Higienizada Inteira
    st.markdown("---")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Baixar base completa de {tipo_atual} higienizada (.csv)",
        data=csv,
        file_name=f"planilha_{tipo_atual.lower().replace(' ', '_')}_marketing_enxuta.csv",
        mime="text/csv"
    )
else:
    st.error(f"⚠️ O arquivo correspondente (`{caminho_arquivo}`) ainda não foi encontrado na raiz do seu repositório no GitHub. Certifique-se de que subiu com esse nome exato!")
