import streamlit as st
import random

def buscar_e_transformar_noticias():
    st.subheader("🌐 Radar Global LocMee & Gerador LocNews")
    st.markdown("Curadoria de inteligência internacional com análise adaptada e exclusiva para o mercado B2B brasileiro.")

    # Banco expandido de matérias cobrindo os pilares do turismo
    banco_noticias = [
        {
            "categoria": "Mercado Aéreo",
            "titulo": "A Nova Rota da Conectividade: Como o Aéreo Regional Está Redesenhando as Vendas B2B",
            "conteudo": (
                "O mercado global de aviação comercial vem registrando uma mudança silenciosa, mas profunda: "
                "companhias aéreas internacionais estão estreitando parcerias diretas com redes e operadores regionais, "
                "ignorando intermediários tradicionais. Para o agente de viagens no Brasil, isso significa tarifas mais competitivas "
                "e maior autonomia para montar pacotes personalizados de saída local.\n\n"
                "_Fonte de referência internacional: Global Aviation Wire_"
            ),
            "analise": (
                "**Análise LocNews:** No ecossistema B2B atual, depender exclusivamente de grandes hubs centralizados engessa a operação das agências brasileiras. "
                "O profissional que dominar essas novas conexões diretas ganha margem de negociação e entrega um produto muito mais ágil para o seu cliente corporativo e de lazer."
            ),
            "fonte": "Global Aviation Wire"
        },
        {
            "categoria": "Setor Marítimo",
            "titulo": "Além do Lazer: O Boom dos Cruzeiros Temáticos e de Luxo na Estratégia das Agências",
            "conteudo": (
                "As tendências globais do setor marítimo apontam para um crescimento exponencial na procura por cruzeiros temáticos, "
                "expedições de nicho e navios de pequeno porte (focados em experiência e exclusividade). Os viajantes de alta renda "
                "estão trocando os resorts tradicionais por roteiros náuticos imersivos.\n\n"
                "_Fonte de referência internacional: Cruise Industry Trends_"
            ),
            "analise": (
                "**Análise LocNews:** Vender cruzeiros deixou de ser apenas a comercialização de cabines em volume; transformou-se em consultoria de estilo de vida. "
                "Para as agências parceiras no Brasil, posicionar esse produto no portfólio eleva o ticket médio consideravelmente e garante uma taxa de fidelização que o turismo convencional raramente alcança."
            ),
            "fonte": "Cruise Industry Trends"
        },
        {
            "categoria": "Operadoras & Distribuição",
            "titulo": "Flexibilidade Dinâmica: O Movimento das Operadoras Globais para Concorrer com as OTAs",
            "conteudo": (
                "Para enfrentar a pressão das grandes plataformas digitais de venda direta (OTAs), as operadoras globais de turismo "
                "estão reformulando seus modelos contratuais e tecnológicos. A palavra de ordem é 'flexibilidade dinâmica', permitindo que o agente "
                "monte itinerários complexos em tempo real com comissionamento garantido.\n\n"
                "_Fonte de referência internacional: Tour Operator Insight_"
            ),
            "analise": (
                "**Análise LocNews:** Esse movimento valida o que sempre defendemos: a tecnologia deve trabalhar a favor da capilaridade humana. "
                "O agente de viagens nacional que une a agilidade de uma plataforma digital à sua capacidade consultiva se torna insubstituível diante de robôs de vendas automatizadas."
            ),
            "fonte": "Tour Operator Insight"
        },
        {
            "categoria": "Tendências & Bem-Estar",
            "titulo": "Turismo de Longevidade: O Novo Perfil de Consumo que Domina os Destinos Exclusivos",
            "conteudo": (
                "O conceito de férias mudou globalmente. O turismo tradicional de correria — focado em visitar dez cidades em cinco dias — "
                "deu espaço ao 'turismo de bem-estar e longevidade'. Retiros de saúde, hotéis-boutique isolados na natureza e programas de "
                "desintoxicação digital lideram as reservas do mercado internacional de alto padrão.\n\n"
                "_Fonte de referência internacional: Wellness Travel Report_"
            ),
            "analise": (
                "**Análise LocNews:** O mercado B2B brasileiro precisa absorver essa demanda urgentemente. Oferecer pacotes focados em saúde preventiva e reconexão "
                "é a chave para atrair um público com alto poder aquisitivo no Brasil, que valoriza cada vez mais a curadoria especializada do agente."
            ),
            "fonte": "Wellness Travel Report"
        }
    ]

    # Botão para sortear/atualizar e trazer exatamente 3 notícias variadas
    if "noticias_selecionadas" not in st.session_state:
        st.session_state["noticias_selecionadas"] = random.sample(banco_noticias, 3)

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        if st.button("🔄 Sortear 3 Novas Matérias para o LocNews"):
            st.session_state["noticias_selecionadas"] = random.sample(banco_noticias, 3)
            st.toast("3 novas matérias sorteadas!", icon="🎯")

    st.markdown("---")

    # Exibição das 3 matérias separando o texto base e a Análise LocNews
    for i, item in enumerate(st.session_state["noticias_selecionadas"], 1):
        with st.container():
            st.markdown(f"### 📰 Matéria #{i}: [{item['categoria']}] {item['titulo']}")
            
            # Caixa 1: Texto principal da matéria pronto para copiar
            st.markdown("**📄 Texto Base para o Blog:**")
            st.text_area(
                label=f"Texto base - {item['titulo']}",
                value=item['conteudo'],
                height=150,
                key=f"texto_base_{i}"
            )
            
            # Caixa 2: Análise exclusiva LocNews adaptada ao mercado brasileiro
            st.markdown("**💡 Análise LocNews (Visão Estratégica B2B):**")
            st.info(item['analise'])
            
            st.markdown("---")
