import streamlit as st
import requests

def buscar_e_transformar_noticias():
    st.subheader("🌐 Radar Global LocMee")
    st.markdown("Curadoria de tendências internacionais adaptadas com exclusividade para o mercado B2B brasileiro.")

    # Simulação de uma busca em API global (ex: World News API / NewsAPI)
    # No futuro, aqui entra a requisição requests.get("https://api.worldnewsapi.com/...")
    
    # Exemplo de payload simulado vindo do mercado internacional (ex: Europa/EUA)
    noticias_globais = [
        {
            "titulo_original": "AI-Powered Itinerary Builders Are Transforming Corporate Travel Agencies",
            "fonte_original": "Global Tourism Tech Review",
            "conteudo_original": "Travel management companies adopting generative AI for custom itineraries are reporting a 40% reduction in planning time and a significant boost in high-end client retention.",
            "categoria": "Tecnologia & Inovação"
        },
        {
            "titulo_original": "B2B Supplier Platforms Shift Toward Direct API Integration for Regional Tour Operators",
            "fonte_original": "World Travelwire",
            "conteudo_original": "Suppliers worldwide are bypassing legacy GDS systems to connect directly with regional B2B networks, speeding up commission settlements and inventory updates.",
            "categoria": "Distribuição B2B"
        }
    ]

    if st.button("🔄 Atualizar Radar Global"):
        with st.spinner("Analisando e traduzindo tendências globais..."):
            # Aqui simulamos a inteligência reescrevendo com a "Cara da LocMee"
            pass

    st.markdown("---")

    # Exibição dos cards customizados no estilo LocMee
    for item in noticias_globais:
        with st.container():
            st.markdown(f"**[{item['categoria']}] {item['titulo_original']}**")
            
            # Aqui entra a mágica: o texto reescrito com a ótica da LocMee
            if "AI-Powered" in item['titulo_original']:
                texto_locmee = (
                    "**Análise LocMee:** O uso de ferramentas baseadas em inteligência artificial para montagem de roteiros "
                    "já é uma realidade irreversível no exterior. Para o agente de viagens e operador B2B no Brasil, o ganho de eficiência "
                    "não substitui o toque consultivo, mas libera o profissional para focar no relacionamento e na alta conversão."
                )
            else:
                texto_locmee = (
                    "**Análise LocMee:** A descentralização de sistemas legados em favor de conexões diretas via API reforça a nossa tese "
                    "de que centralizar informações e contatos estratégicos é o único caminho para dar agilidade real ao trade turístico."
                )

            st.info(texto_locmee)
            st.caption(f"Fonte original de referência: *{item['fonte_original']}*")
            st.markdown("")
