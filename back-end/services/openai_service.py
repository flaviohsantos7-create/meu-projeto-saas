import json

def gerar_estratégia_bilíngue(dados_brutos, client):

    tema = dados_brutos.get('tema', 'Não informado')
    problema = dados_brutos.get('problema', 'Não informado')
    termos = dados_brutos.get('termos', '')
    contexto = dados_brutos.get('contexto', '')
    cenario = dados_brutos.get('cenario', 'Não especificado')

    prompt = f"""
    Como um especialista em bibliometria, analise o seguinte pedido de pesquisa:
    Cenário de Aplicação: {cenario} 
    Tema: {tema}
    Problema: {problema}
    Termos: {termos}
    Contexto: {contexto}

    REGRAS CRÍTICAS DE LÓGICA E TAMANHO (EVITE ERROS DE API):
    1. A string DEVE SER EXTREMAMENTE CURTA E CONCISA. Strings longas quebram os servidores das bases de dados.
    2. Limite ABSOLUTO: Use no MÁXIMO 3 blocos conectados por 'AND'.
    3. Dentro de cada bloco, use no MÁXIMO 2 ou 3 sinônimos conectados por 'OR'.
    4. Exemplo perfeito e seguro: ("Generative AI" OR "Machine Learning") AND ("Higher Education" OR "University") AND ("Ethics")
    5. Priorize apenas os termos técnicos nucleares.
    6. Crie um título bem curto (máximo 5 palavras) que resuma o NÚCLEO da pesquisa para ser usado no histórico do sistema.

    Gere um JSON com a seguinte estrutura:
    {{
        "titulo_historico": "Um título curto (máximo 5 palavras)",
        "string_pt": "String curta em português (Ex: ('termo1' OR 'sinônimo') AND ('contexto'))",
        "contexto_pt": "Resumo do contexto técnico em português detalhado",
        "string_en": "String curta em inglês (Ex: ('term1' OR 'synonym') AND ('context'))",
        "contexto_en": "Summary of the technical context in English"
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" },
        temperature=0.1
    )
    
    return json.loads(response.choices[0].message.content)

#_________________________________________________________________________________________________________________________________________________

def filtrar_artigos_ia_unificado(tema, contexto_en, contexto_pt, artigos, client):

    if not artigos:
        return []

    lista_simplificada = []
    
    # TRUQUE DE ENGENHARIA: Pré-processamento cego para a IA
    termos_bloqueio = ["restrito", "indisponível", "não disponível", "não informados"]
    
    for i, art in enumerate(artigos):
        resumo_atual = art.get('resumo', '')
        
        # Se o Python detectar que é um resumo falso/bloqueado, injeta o comando direto
        if not resumo_atual or any(termo in resumo_atual.lower() for termo in termos_bloqueio):
            resumo_ia = "[SEM RESUMO - AVALIAR ESTE ARTIGO EXCLUSIVAMENTE PELO TITULO]"
        else:
            resumo_ia = resumo_atual[:400]

        lista_simplificada.append({
            "id_temp": i,
            "titulo": art.get('titulo', ''),
            "resumo": resumo_ia
        })

    prompt = f"""
    Você é um avaliador acadêmico implacável. Avalie a relevância de cada artigo em relação ao escopo da pesquisa.
    
    TEMA CENTRAL DA PESQUISA: {tema}
    ESCOPO DE CONTEXTO (PT): {contexto_pt}
    ESCOPO DE CONTEXTO (EN): {contexto_en}

    LISTA DE ARTIGOS:
    {json.dumps(lista_simplificada, ensure_ascii=False)}

    ALGORITMO DE AVALIAÇÃO OBRIGATÓRIO (PASSO A PASSO):
    Para cada artigo, verifique a chave "resumo" e aplique OBRIGATORIAMENTE um dos dois cenários:
    
    CENÁRIO A (Quando há texto de resumo real):
    - Regra: Compare o TÍTULO e o RESUMO com o TEMA e o CONTEXTO.
    - Justificativa: Comece OBRIGATORIAMENTE com a frase "Avaliando resumo: " e explique a conexão.
    
    CENÁRIO B (Quando a chave resumo for O EXATO TEXTO "[SEM RESUMO - AVALIAR ESTE ARTIGO EXCLUSIVAMENTE PELO TITULO]"):
    - Regra: IGNORE o contexto. Compare APENAS O TÍTULO do artigo com o TEMA CENTRAL da pesquisa.
    - Nota: Se o título for diretamente ligado ao tema, dê nota entre 80 e 100. Se for conexo, 40 a 70. Se for fora do tema, 0 a 30.
    - Justificativa: Comece OBRIGATORIAMENTE com a frase "Avaliando pelo título: " e justifique usando as palavras do título. JAMAIS diga que não pôde avaliar.

    TAREFA:
    Retorne um objeto JSON contendo as notas (0 a 100) e justificativas (máximo 45 palavras) aplicando os cenários acima.
    
    FORMATO DE SAÍDA:
    {{"avaliacoes": [ {{"id_temp": 0, "nota": 85, "justificativa": "..."}}, ... ]}}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um classificador algorítmico rigoroso. Siga a condicional de Cenário A e Cenário B estritamente. Responda apenas em JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        resultado_ia = json.loads(response.choices[0].message.content)
        avaliacoes = {item['id_temp']: item for item in resultado_ia.get('avaliacoes', [])}

        artigos_finais = []
        for i, art in enumerate(artigos):
            info_ia = avaliacoes.get(i, {"nota": 0, "justificativa": "Erro na avaliação algorítmica."})
            artigos_finais.append({**art, **info_ia})
        
        return artigos_finais

    except Exception as e:
        print(f"Erro na filtragem em lote: {e}")
        return [{**art, "nota": 0, "justificativa": "Erro no processamento da IA."} for art in artigos]
