import streamlit as st
import pandas as pd

# Configuração da página para aproveitar bem o espaço (ótimo para mobile)
st.set_page_config(page_title="LocMee Data Processor", layout="wide")

st.title("🔄 LocMee Data Processor (v3.3)")
st.markdown("Higienização, ordenação inteligente e consulta rápida para o trade turístico.")

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
        alvos = []

    novas_cols = [c for c in alvos if c in cols] + [c for c in cols if c not in alvos]
    return df[novas_cols]

# Upload do arquivo
uploaded_file = st.file_uploader("Arraste a planilha (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Barra de progresso / Spinner de carregamento do arquivo
    with st.spinner("🔄 Processando e higienizando os dados da planilha..."):
        df = pd.read_excel(uploaded_file)
        
        nome_arquivo = uploaded_file.name.lower()
        if "guia" in nome_arquivo:
            tipo_atual = "Guias de Turismo"
        elif "hospedagem" in nome_arquivo or "hotel" in nome_arquivo:
            tipo_atual = "Meio de Hospedagem"
        elif "locadora" in nome_arquivo or "veiculo" in nome_arquivo:
            tipo_atual = "Locadora de Veículos"
        else:
            tipo_atual = "Agências de Turismo"

        df = reorganizar_colunas(df, tipo_atual)

    st.success(f"Planilha processada com sucesso! Categoria detectada: **{tipo_atual}**")
    
    # Pré-visualização com 5 linhas
    st.write("📋 **Pré-visualização (5 primeiras linhas):**")
    st.dataframe(df.head(5), use_container_width=True)
    if len(df) > 5:
        st.caption("Mostrando as primeiras 5 linhas na prévia. O arquivo baixado conterá todos os registros.")

    st.markdown("---")
    
    # Seção de Busca Rápida e Ficha de Contato
    st.subheader("🔍 Consulta e Ficha de Cadastro")
    st.markdown("Busque por parte do **Nome** ou **CNPJ / Inscrição** para gerar o cartão de contato rápido.")
    
    termo_busca = st.text_input("Digite o CNPJ, Nome Fantasia ou Responsável:")

    if termo_busca:
        # Reloginho logo abaixo do input de busca indicando o trabalho em tempo real
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
                inscricao = achar_valor(["cnpj", "inscrição", "cpf", "registro"])
                responsavel = achar_valor(["responsável", "contato", "sócio", "proprietário"])
                telefone = achar_valor(["telefones", "telefone", "celular", "whatsapp", "fone"])
                email = achar_valor(["e-mail", "email", "correio"])

                ficha_texto = (
                    f"🏢 Nome: {nome_fantasia}\n"
                    f"📄 Inscrição/CNPJ: {inscricao}\n"
                    f"👤 Responsável: {responsavel}\n"
                    f"📞 Telefone: {telefone}\n"
                    f"📧 E-mail: {email}"
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
        label="📥 Baixar planilha processada completa (.csv)",
        data=csv,
        file_name="planilha_locmee_higienizada.csv",
        mime="text/csv"
    )
