# -*- coding: utf-8 -*-
# VERSÃO: 1.9
import streamlit as st
import pandas as pd
import io
import time

# --- CACHE PARA OTIMIZAÇÃO (LÊ TODAS AS ABAS E UNE) ---
@st.cache_data
def carregar_dados(arquivo):
    xls = pd.ExcelFile(arquivo)
    dfs = []
    for sheet in xls.sheet_names:
        df_temp = pd.read_excel(xls, sheet_name=sheet)
        if not df_temp.empty:
            dfs.append(df_temp)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="LocMee Data Processor | Web v1.9", page_icon="🔄", layout="centered")

def Autenticar():
    if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        st.subheader("Acesso Restrito - LocMee Data")
        with st.form("form_login"):
            senha = st.text_input("Insira a senha de acesso comercial:", type="password")
            submit = st.form_submit_button("Entrar")
            if submit:
                if senha == st.secrets["SENHA_ACESSO"]:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else: st.error("Senha incorreta.")
        return False
    return True

# --- FUNÇÃO DE HIGIENIZAÇÃO UNIFICADA (MARKETING) ---
def processar_higienizacao_marketing(df_orig, barra):
    df_mkt = df_orig.copy()
    barra.progress(30, text="Higienizando nomes (30%)...")
    
    col_nome = next((c for c in df_mkt.columns if any(x in c.lower() for x in ['nome completo', 'nome', 'responsável', 'razão'])), None)
    if col_nome:
        def limpar_nome(nome):
            if pd.isna(nome): return ""
            partes = [p for p in str(nome).split() if p.lower() not in ['de', 'da', 'do', 'das', 'dos', 'di']]
            return " ".join(partes[:2])
        df_mkt['Nome'] = df_mkt[col_nome].apply(limpar_nome)
    else:
        df_mkt['Nome'] = ""
    
    barra.progress(70, text="Processando e higienizando e-mails (70%)...")
    cols_email = [c for c in df_mkt.columns if 'email' in c.lower() or 'e-mail' in c.lower()]
    def escolher_melhor_email(row):
        emails = [str(row[c]).lower().replace('|', '').strip() for c in cols_email if pd.notna(row[c]) and "@" in str(row[c])]
        if not emails: return ""
        prioridade = ['corporativo', 'hotmail', 'gmail', 'outlook']
        for p in prioridade:
            for e in emails:
                if p in e: return e
        return emails[0]

    if cols_email:
        df_mkt['Email'] = df_mkt.apply(escolher_melhor_email, axis=1)
    else:
        df_mkt['Email'] = ""
    
    barra.progress(100, text="Higienização concluída (100%)!")
    return df_mkt[['Nome', 'Email']]

# --- FLUXO PRINCIPAL ---
if Autenticar():
    st.title("🔄 LocMee Data Processor (v1.9)")
    
    progresso_container = st.container()
    barra_global = progresso_container.progress(0, text="Aguardando upload da planilha (0%)...")
    
    st.write("---")
    arquivo_enviado = st.file_uploader("Arraste a planilha (.xlsx)", type=["xlsx"])

    if arquivo_enviado is not None:
        barra_global.progress(25, text="Lendo e unificando abas do Excel (25%)...")
        df_completo = carregar_dados(arquivo_enviado)
        
        barra_global.progress(50, text="Identificando atividade turística (50%)...")
        valor_atividade = str(df_completo.iloc[0, 0]).strip() if not df_completo.empty else ""
        
        if "Guia" in valor_atividade:
            tipo_planilha = "Guias"
        elif "Hospedagem" in valor_atividade:
            tipo_planilha = "Hospedagens"
        elif "Locadora" in valor_atividade:
            tipo_planilha = "Locadoras"
        elif "Agência" in valor_atividade:
            tipo_planilha = "Agências"
        else:
            tipo_planilha = "Geral"
            
        df_completo.columns = [str(c).strip() for c in df_completo.columns]
        barra_global.progress(100, text="Planilhas carregadas e unificadas com sucesso! (100%)")
        st.success(f"Planilha: **{tipo_planilha}** | Base Total Unificada: {len(df_completo)} registros.")

        # --- FILTROS COMUNS (ESTADO E MUNICÍPIO) ---
        st.subheader("Filtros Gerais")
        col1, col2 = st.columns(2)
        with col1:
            uf_sel = st.selectbox("UF:", ["Todos"] + sorted(df_completo['UF'].dropna().unique().tolist())) if 'UF' in df_completo.columns else "Todos"
        with col2:
            col_mun = 'Município' if 'Município' in df_completo.columns else ('Município de Atuação' if 'Município de Atuação' in df_completo.columns else None)
            muns = sorted(df_completo[col_mun].dropna().unique().tolist()) if col_mun and col_mun in df_completo.columns else []
            mun_sel = st.selectbox("Município:", ["Todos"] + muns)

        # --- FILTROS ESPECÍFICOS POR ATIVIDADE ---
        cat_sel, guia_cat_sel, guia_seg_sel, hosp_tipo_sel, hosp_uh_sel, loc_veiculo_sel = "Todas", "Todas", "Todas", "Todos", "Todas", "Todas"

        if tipo_planilha == "Agências":
            st.subheader("Filtros Específicos - Agências")
            cat_opcoes = ["Todas", "Agências", "Operadoras"]
            cat_sel = st.selectbox("Categoria de Atuação:", cat_opcoes)
            
        elif tipo_planilha == "Guias":
            st.subheader("Filtros Específicos - Guias de Turismo")
            c_guia1, c_guia2 = st.columns(2)
            with c_guia1:
                cat_guia_vals = sorted(df_completo['Categoria(s)'].dropna().unique().tolist()) if 'Categoria(s)' in df_completo.columns else []
                guia_cat_sel = st.selectbox("Categoria(s):", ["Todas"] + cat_guia_vals)
            with c_guia2:
                seg_guia_vals = sorted(df_completo['Segmento(s)'].dropna().unique().tolist()) if 'Segmento(s)' in df_completo.columns else []
                guia_seg_sel = st.selectbox("Segmento(s):", ["Todas"] + seg_guia_vals)
                
        elif tipo_planilha == "Hospedagens":
            st.subheader("Filtros Específicos - Meios de Hospedagem")
            c_hosp1, c_hosp2 = st.columns(2)
            with c_hosp1:
                tipo_hosp_vals = sorted(df_completo['Tipo de Hospedagem'].dropna().unique().tolist()) if 'Tipo de Hospedagem' in df_completo.columns else []
                hosp_tipo_sel = st.selectbox("Tipo de Hospedagem:", ["Todos"] + tipo_hosp_vals)
            with c_hosp2:
                hosp_uh_sel = st.selectbox("Unidades Habitacionais (UHs):", [
                    "Todas", 
                    "Até 20 UHs", 
                    "De 21 a 50 UHs", 
                    "De 51 a 100 UHs", 
                    "De 101 a 200 UHs", 
                    "Acima de 201 UHs"
                ])
                
        elif tipo_planilha == "Locadoras":
            st.subheader("Filtros Específicos - Locadoras de Veículos")
            col_veic = next((c for c in df_completo.columns if 'terrestre' in c.lower() or ('veículo' in c.lower() and 'aquático' not in c.lower() and 'aquatico' not in c.lower())), None)
            if col_veic:
                veic_vals = sorted(df_completo[col_veic].dropna().unique().tolist())
                loc_veiculo_sel = st.selectbox("Tipo de Veículos - Terrestres:", ["Todos"] + veic_vals)

        # --- AÇÃO DE PROCESSAR ---
        if st.button("🚀 PROCESSAR LOTE"):
            barra_proc = progresso_container.progress(0, text="Iniciando filtragem (0%)...")
            
            df_trabalho = df_completo.copy()
            barra_proc.progress(25, text="Aplicando filtros geográficos (25%)...")
            if uf_sel != "Todos": df_trabalho = df_trabalho[df_trabalho['UF'] == uf_sel]
            if mun_sel != "Todos" and col_mun: df_trabalho = df_trabalho[df_trabalho[col_mun] == mun_sel]
            
            barra_proc.progress(50, text="Aplicando filtros específicos da atividade (50%)...")
            if tipo_planilha == "Agências":
                if cat_sel == "Agências":
                    df_trabalho = df_trabalho[df_trabalho['Categoria de Atuação'].str.contains('Agência de Viagens', na=False) & ~df_trabalho['Categoria de Atuação'].str.contains('Operadoras', na=False)]
                elif cat_sel == "Operadoras":
                    df_trabalho = df_trabalho[df_trabalho['Categoria de Atuação'].str.contains('Operadoras Turísticas', na=False)]
            elif tipo_planilha == "Guias":
                if guia_cat_sel != "Todas": df_trabalho = df_trabalho[df_trabalho['Categoria(s)'] == guia_cat_sel]
                if guia_seg_sel != "Todas": df_trabalho = df_trabalho[df_trabalho['Segmento(s)'] == guia_seg_sel]
            elif tipo_planilha == "Hospedagens":
                if hosp_tipo_sel != "Todos": df_trabalho = df_trabalho[df_trabalho['Tipo de Hospedagem'] == hosp_tipo_sel]
                if hosp_uh_sel != "Todas" and 'Unidades Habitacionais' in df_trabalho.columns:
                    def filtrar_uh(val):
                        try:
                            num = int(val)
                        except:
                            return False
                        if hosp_uh_sel == "Até 20 UHs": return num <= 20
                        elif hosp_uh_sel == "De 21 a 50 UHs": return 21 <= num <= 50
                        elif hosp_uh_sel == "De 51 a 100 UHs": return 51 <= num <= 100
                        elif hosp_uh_sel == "De 101 a 200 UHs": return 101 <= num <= 200
                        elif hosp_uh_sel == "Acima de 201 UHs": return num >= 201
                        return True
                    df_trabalho = df_trabalho[df_trabalho['Unidades Habitacionais'].apply(filtrar_uh)]
            elif tipo_planilha == "Locadoras" and col_veic:
                if loc_veiculo_sel != "Todos": df_trabalho = df_trabalho[df_trabalho[col_veic] == loc_veiculo_sel]

            barra_proc.progress(85, text="Salvando estado do processamento (85%)...")
            st.session_state["df_final"] = df_trabalho
            st.session_state["tipo"] = tipo_planilha
            st.session_state["cat_sel"] = cat_sel
            st.session_state["uf_sel"] = uf_sel
            
            barra_proc.progress(100, text="Processamento concluído com sucesso! (100%)")
            time.sleep(0.5)
            st.rerun()

        # --- ÁREA DE PRÉVIA E DOWNLOAD ---
        if "df_final" in st.session_state:
            df = st.session_state["df_final"]
            tipo = st.session_state["tipo"]
            cat = st.session_state.get("cat_sel", "Todas")
            uf = st.session_state.get("uf_sel", "Geral")
            
            st.write("---")
            st.subheader("👁️ Prévia dos Dados Processados")
            st.write(f"Total de registros encontrados após os filtros: **{len(df)}**")
            
            # Exibe a prévia interativa na tela
            st.dataframe(df.head(5), use_container_width=True)
            if len(df) > 5:
                st.caption("Mostrando as primeiras 100 linhas na prévia. O arquivo baixado conterá todos os registros.")

            st.write("---")
            st.subheader("✅ Download de Arquivos")
            
            barra_down = progresso_container.progress(0, text="Iniciando geração dos relatórios (0%)...")
            
            barra_down.progress(40, text="Gerando planilha Completa/Geral (40%)...")
            output_comp = io.BytesIO()
            with pd.ExcelWriter(output_comp, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Geral", index=False)
            
            barra_down.progress(70, text="Processando Enxuta/Marketing (70%)...")
            df_enxuto = processar_higienizacao_marketing(df, barra_down)
            
            output_enx = io.BytesIO()
            with pd.ExcelWriter(output_enx, engine='openpyxl') as writer:
                if tipo == "Agências" and cat == "Todas":
                    df_ag = df_enxuto[df['Categoria de Atuação'].str.contains('Agência de Viagens', na=False) & ~df['Categoria de Atuação'].str.contains('Operadoras', na=False)]
                    df_op = df_enxuto[df['Categoria de Atuação'].str.contains('Operadoras Turísticas', na=False)]
                    df_ag.to_excel(writer, sheet_name="Agências", index=False)
                    df_op.to_excel(writer, sheet_name="Operadoras", index=False)
                else:
                    df_enxuto.to_excel(writer, sheet_name="Marketing", index=False)

            barra_down.progress(100, text="Arquivos prontos para download! (100%)")

            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📥 BAIXAR COMPLETA", output_comp.getvalue(), f"locmee_completa_{tipo}_{uf}_{cat}.xlsx")
            with c2:
                st.download_button("📥 BAIXAR ENXUTA", output_enx.getvalue(), f"locmee_enxuta_{tipo}_{uf}_{cat}.xlsx")
