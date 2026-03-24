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
    Use este cenário para refinar a string booleana e o contexto.
    Tema: {tema}
    Problema: {problema}
    Termos: {termos}
    Contexto: {contexto}

    DIRETRIZES DE LÓGICA BOOLEANA:
    1. Priorize o operador 'OR' para agrupar sinônimos, variações gramaticais e termos correlatos.
    2. Use o operador 'AND' APENAS para conectar conceitos diferentes (ex: Tema AND Tecnologia AND Localização).
    3. Evite strings restritivas demais. Se o usuário forneceu termos variados para o mesmo conceito, eles DEVEM estar entre parênteses unidos por 'OR'.
    4. Garanta que a string em inglês utilize termos técnicos (MeSH/Emtree) quando apropriado.

    Gere um JSON com a seguinte estrutura:
    {{
        "string_pt": "String booleana em português (ex: ('termo1' OR 'sinônimo') AND ('contexto1' OR 'contexto2'))",
        "contexto_pt": "Resumo do contexto técnico em português para comparação e filtragem semântica, resumo bem estruturado com e rico em detalhes",
        "string_en": "String booleana em inglês técnico (ex: ('term1' OR 'synonym') AND ('context1' OR 'context2'))",
        "contexto_en": "Summary of the technical context in English for semantic comparison and filtering; a well-structured summary rich in detail"
    }}
    """
    
    # Adicionado temperature=0.1 para acelerar e dar respostas mais determinísticas
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" },
        temperature=0.1
    )
    

    return json.loads(response.choices[0].message.content)
#_________________________________________________________________________________________________________________________________________________
def filtrar_artigos_ia_unificado(contexto_en, contexto_pt, artigos, client):

    if not artigos:
        return []

    lista_simplificada = []
    for i, art in enumerate(artigos):
        lista_simplificada.append({
            "id_temp": i,
            "titulo": art['titulo'],
            "resumo": art['resumo'][:400] # Otimizado: Reduzido de 500 para 400 para acelerar o processamento
        })

    prompt = f"""
    Você é um avaliador acadêmico. Analise a lista de artigos abaixo comparando-os com o escopo da pesquisa.
    
    ESCOPO (PT): {contexto_pt}
    ESCOPO (EN): {contexto_en}

    LISTA DE ARTIGOS:
    {json.dumps(lista_simplificada, ensure_ascii=False)}

    TAREFA:
    Para cada artigo, retorne uma nota (0-100) e uma justificativa de no máximo 50 palavras em Português. Seja direto e técnico
    
    RETORNO OBRIGATÓRIO (JSON):
    Retorne um objeto JSON com uma chave "avaliacoes" contendo uma lista de objetos:
    {{"avaliacoes": [ {{"id_temp": 0, "nota": 85, "justificativa": "..."}}, ... ]}}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente de pesquisa eficiente que responde apenas em JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1 # Adicionado para forçar a IA a ir direto ao ponto rapidamente
        )
        
        resultado_ia = json.loads(response.choices[0].message.content)
        avaliacoes = {item['id_temp']: item for item in resultado_ia.get('avaliacoes', [])}

        artigos_finais = []
        for i, art in enumerate(artigos):
            info_ia = avaliacoes.get(i, {"nota": 0, "justificativa": "Não avaliado pela IA."})
            artigos_finais.append({**art, **info_ia})
        
        return artigos_finais

    except Exception as e:
        print(f"Erro na filtragem em lote: {e}")
        return [{**art, "nota": 0, "justificativa": "Erro no processamento."} for art in artigos]
#_________________________________________________________________________________________________________________________________________________