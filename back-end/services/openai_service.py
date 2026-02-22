import json

def gerar_estratégia_bilíngue(dados_brutos, client):

    tema = dados_brutos.get('tema', 'Não informado')
    problema = dados_brutos.get('problema', 'Não informado')
    termos = dados_brutos.get('termos', '')
    contexto = dados_brutos.get('contexto', '')

    prompt = f"""
    Como um especialista em bibliometria, analise o seguinte pedido de pesquisa:
    Tema: {tema}
    Problema: {problema}
    Termos: {termos}
    Contexto: {contexto}

    Gere um JSON com a seguinte estrutura:
    {{
        "string_pt": "String booleana em português para Crossref/SciELO" (ex: "Termo A" OR "Termo B" / a depender das semelhanças de termos ou complementos de termos usar o AND do jeito que ficaria melhor para uma pesquisa),
        "contexto_pt": "Resumo do contexto em português",
        "string_en": "String booleana em inglês técnico para PubMed/arXiv" (ex: "Termo A" OR "Termo B" / a depender das semelhanças de termos ou complementos de termos usar o AND do jeito que ficaria melhor para uma pesquisa),
        "contexto_en": "Resumo do contexto em inglês para filtragem de resumos"
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
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
            "resumo": art['resumo'][:500]
        })

    prompt = f"""
    Você é um avaliador acadêmico. Analise a lista de artigos abaixo comparando-os com o escopo da pesquisa.
    
    ESCOPO (PT): {contexto_pt}
    ESCOPO (EN): {contexto_en}

    LISTA DE ARTIGOS:
    {json.dumps(lista_simplificada, ensure_ascii=False)}

    TAREFA:
    Para cada artigo da lista, atribua uma nota de 0 a 100 e uma justificativa curta em Português.
    
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
            response_format={"type": "json_object"}
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