import streamlit as st
import random

def buscar_e_transformar_noticias():
    st.subheader("🌐 Radar Global LocMee & Gerador LocNews")
    st.markdown("Curadoria de inteligência internacional aprofundada (leitura de 1-2 min) e adaptada para o mercado B2B brasileiro.")

    # Banco de matérias aprofundadas cobrindo os pilares do turismo
    banco_noticias = [
        {
            "categoria": "Mercado Aéreo",
            "titulo": "A Nova Rota da Conectividade: Como o Aéreo Regional Está Redesenhando as Vendas B2B",
            "conteudo": (
                "O mercado global de aviação comercial vem registrando uma mudança silenciosa, mas profunda na dinâmica de distribuição de bilhetes e acordos comerciais. "
                "Grandes companhias aéreas internacionais estão reestruturando suas malhas e estreitando parcerias diretas com redes e operadores regionais, "
                "buscando rotas alternativas que contornem a alta concentração dos grandes aeroportos centrais.\n\n"
                "Essa descentralização traz reflexos diretos para o ecossistema de viagens. Ao negociar bilhetes e bloqueios de forma mais próxima às bases locais, "
                "as empresas aéreas conseguem preencher aeronaves em voos sazonais e de média distância, enquanto os mercados regionais ganham competitividade em tarifas. "
                "Para os profissionais que operam no dia a dia do turismo, essa tendência abre uma janela estratégica valiosa para a criação de pacotes customizados de saída local, "
                "reduzindo custos logísticos com deslocamentos internos desnecessários para o passageiro.\n\n"
                "_Fonte de referência internacional: Global Aviation Wire_"
            ),
            "analise": (
                "**Análise LocNews:** No ecossistema B2B atual, depender exclusivamente de grandes hubs centralizados engessa a operação das agências e operadores. "
                "O profissional que passar a olhar para essas novas conexões diretas ganha margem real de negociação e consegue entregar um produto muito mais ágil e competitivo para o cliente final."
            ),
            "fonte": "Global Aviation Wire"
        },
        {
            "categoria": "Setor Marítimo",
            "titulo": "Além do Lazer: O Boom dos Cruzeiros Temáticos e de Luxo na Estratégia das Agências",
            "conteudo": (
                "As tendências globais do setor marítimo apontam para um crescimento exponencial e contínuo na procura por cruzeiros temáticos, expedições de nicho "
                "e embarcações de pequeno e médio porte, fortemente voltadas para a experiência imersiva e a exclusividade. Enquanto o turismo de massa busca volume, "
                "o segmento náutico de alto padrão tem atraído viajantes dispostos a investir mais em roteiros diferenciados.\n\n"
                "Esse movimento reflete uma mudança drástica no comportamento de consumo pós-pandemia: o foco absoluto na vivência e na personalização. "
                "Armadoras internacionais estão investindo em rotas que incluem paradas prolongadas, experiências culturais profundas a bordo e serviços ultra-personalizados. "
                "Para o trade turístico, comercializar esse formato exige uma consultoria especializada, transformando a venda de uma simples cabine em uma experiência inesquecível de viagem.\n\n"
                "_Fonte de referência internacional: Cruise Industry Trends_"
            ),
            "analise": (
                "**Análise LocNews:** Vender cruzeiros deixou de ser apenas a comercialização de bilhetes em massa; transformou-se em uma consultoria completa de estilo de vida. "
                "Para as agências parceiras no Brasil, posicionar esse produto no portfólio eleva o ticket médio consideravelmente e garante uma taxa de fidelização que o turismo convencional raramente alcança."
            ),
            "fonte": "Cruise Industry Trends"
        },
        {
            "categoria": "Operadoras & Distribuição",
            "titulo": "Flexibilidade Dinâmica: O Movimento das Operadoras Globais para Concorrer com as OTAs",
            "conteudo": (
                "Para enfrentar a pressão constante exercida pelas grandes plataformas digitais de venda direta ao consumidor (OTAs), as operadoras globais de turismo "
                "estão promovendo uma verdadeira revolução em seus modelos contratuais e arquiteturas tecnológicas. A palavra de ordem no mercado internacional é 'flexibilidade dinâmica'.\n\n"
                "Isso significa abandonar pacotes engessados e permitir que redes de distribuição e agências parceiras montem itinerários complexos, combinando hospedagem, "
                "transfers e experiências exclusivas em tempo real com regras de cancelamento flexíveis e comissionamento garantido. A tecnologia deixa de ser uma barreira "
                "e passa a ser o motor de integração entre o fornecedor global e o agente local, que passa a ter armas paritárias de competição no ambiente digital.\n\n"
                "_Fonte de referência internacional: Tour Operator Insight_"
            ),
            "analise": (
                "**Análise LocNews:** Esse movimento valida a tese central da LocMee: a tecnologia deve trabalhar sempre a favor da capilaridade humana. "
                "O agente de viagens nacional que une a agilidade de uma plataforma digital integrada à sua capacidade consultiva se torna absolutamente insubstituível diante de robôs de vendas padronizadas."
            ),
            "fonte": "Tour Operator Insight"
        },
        {
            "categoria": "Tendências & Bem-Estar",
            "titulo": "Turismo de Longevidade: O Novo Perfil de Consumo que Domina os Destinos Exclusivos",
            "conteudo": (
                "O conceito global de férias sofreu uma mutação irreversível. O turismo tradicional de correria — caracterizado por roteiros exaustivos de visitação a múltiplos destinos em poucos dias — "
                "perdeu espaço para o chamado 'turismo de bem-estar e longevidade'. Retiros de saúde preventiva, hotéis-boutique isolados em contato direto com a natureza "
                "e programas focados em desintoxicação digital lideram com folga as planilhas de reservas do mercado internacional de alto padrão.\n\n"
                "Os viajantes buscam agora propriedades e destinos que promovam o reequilíbrio físico e mental, integrando gastronomia orgânica, medicina integrativa e práticas de mindfulness. "
                "Essa mudança de paradigma exige das redes hoteleiras e operadoras uma curadoria muito mais refinada e focada em propósitos de vida, alterando completamente o perfil dos roteiros ofertados.\n\n"
                "_Fonte de referência internacional: Wellness Travel Report_"
            ),
            "analise": (
                "**Análise LocNews:** O mercado B2B brasileiro precisa absorver e antecipar essa demanda urgentemente. Oferecer pacotes focados em saúde preventiva e reconexão "
                "é a chave mestra para atrair um público nacional com altíssimo poder aquisitivo que valoriza profundamente a curadoria especializada do agente de viagens."
            ),
            "fonte": "Wellness Travel Report"
        }
    ]

    # Botão para sortear/atualizar e trazer exatamente 3 matérias completas
    if "noticias_selecionadas" not in st.session_state:
        st.session_state["noticias_selecionadas"] = random.sample(banco_noticias, 3)

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        if st.button("🔄 Sortear 3 Novas Matérias para o LocNews"):
            st.session_state["noticias_selecionadas"] = random.sample(banco_noticias, 3)
            st.toast("3 novas matérias aprofundadas sorteadas!", icon="🎯")

    st.markdown("---")

    # Exibição das 3 matérias formatadas para o blog e análise comercial
    for i, item in enumerate(st.session_state["noticias_selecionadas"], 1):
        with st.container():
            st.markdown(f"### 📰 Matéria #{i}: [{item['categoria']}]")
            
            # Título com opção de toque/cópia facilitada
            st.markdown(f"**Título da Matéria:**")
            st.text_area(
                label=f"Título - {i}",
                value=item['titulo'],
                height=70,
                key=f"titulo_box_{i}"
            )
            
            # Texto principal robusto pronto para o blog
            st.markdown("**📄 Texto Base Completo para o Blog (Leitura de 1-2 min):**")
            st.text_area(
                label=f"Texto base - {item['titulo']}",
                value=item['conteudo'],
                height=240,
                key=f"texto_base_{i}"
            )
            
            # Análise exclusiva LocNews adaptada ao mercado brasileiro
            st.markdown("**💡 Análise LocNews (Visão Estratégica B2B):**")
            st.info(item['analise'])
            
            st.markdown("---")
