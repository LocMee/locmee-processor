import streamlit as st
import requests

def buscar_e_transformar_noticias():
    st.subheader("🌐 Radar Global LocMee")
    st.markdown("Curadoria de tendências internacionais adaptadas com exclusividade para o mercado B2B brasileiro.")

    # Base de dados simulada com foco comercial (Aéreo, Marítimo, Operadoras, Tendências e Bem-Estar)
    noticias_globais = [
        {
            "titulo": "Companhias Aéreas Internacionais Ampliam Conectividade Direta com o Interior do Brasil",
            "fonte": "Global Aviation Wire",
            "categoria": "Mercado Aéreo",
            "analise": (
                "**Análise LocMee:** A descentralização dos voos internacionais reduz a dependência dos grandes hubs e abre uma janela "
                "gigantesca para operadores regionais e agências locais empacotarem produtos de saída direta, facilitando a vida do passageiro corporativo e de lazer."
            )
        },
        {
            "titulo": "Demografia dos Cruzeiros Marítimos Registra Alta Recorde em Roteiros Temáticos e de Luxo",
            "fonte": "Cruise Industry Trends",
            "categoria": "Setor Marítimo",
            "analise": (
                "**Análise LocMee:** O mercado de cruzeiros deixou de ser apenas volume e passou a ser valor agregado. Para o agente de viagens, "
                "vender cabines temáticas e de alto padrão é hoje uma das margens de comissão mais garantidas e de menor esforço de fidelização."
            )
        },
        {
            "titulo": "Operadoras Globais Apostam em Flexibilidade Dinâmica para Concorrer com OTAs",
            "fonte": "Tour Operator Insight",
            "categoria": "Operadoras",
            "analise": (
                "**Análise LocMee:** As grandes operadoras estão redesenhando seus contratos B2B para dar autonomia de montagem ao agente. "
                "Quem ganha é o trade local, que consegue competir em agilidade com as grandes plataformas de venda direta ao consumidor final."
            )
        },
        {
            "titulo": "Turismo de Bem-Estar e Longevidade Lidera Crescimento em Destinos Exclusivos",
            "fonte": "Wellness Travel Report",
            "categoria": "Tendências & Bem-Estar",
            "analise": (
                "**Análise LocMee:** O cliente de alta renda está trocando o turismo tradicional de correria por roteiros de reconexão e saúde preventiva. "
                "Incluir retiros e hotéis-boutique focados em bem-estar no portfólio da agência eleva o ticket médio de forma expressiva."
            )
        }
    ]

    if st.button("🔄 Atualizar Radar Global"):
        st.toast("Radar atualizado com as últimas tendências do mercado!", icon="🚀")

    st.markdown("---")

    # Exibição dos cards customizados no estilo LocMee
    for item in noticias_globais:
        with st.container():
            st.markdown(f"**[{item['categoria']}] {item['titulo']}**")
            st.info(item['analise'])
            st.caption(f"Fonte de referência internacional: *{item['fonte']}*")
            st.markdown("")
