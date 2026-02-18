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

    avaliados = []
    
    for art in artigos:
        prompt = f"""
        OBJETIVO: Avaliar a compatibilidade de um artigo científico com o escopo da pesquisa.
        
        ESCOPO DA PESQUISA (PT): {contexto_pt}
        ESCOPO DA PESQUISA (EN): {contexto_en}
        
        DADOS DO ARTIGO:
        Título: {art['titulo']}
        Resumo: {art['resumo']}
        Fonte: {art.get('fonte', 'N/A')}
        
        TAREFA:
        1. Compare o artigo com o escopo (em ambas as línguas).
        2. Atribua uma nota de 0 a 100.
        3. Justifique em Português por que este artigo é relevante ou não.
        
        RETORNO: Responda apenas com um JSON no formato:
        {{"nota": int, "justificativa": "string"}}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "Você é um assistente de pesquisa científica bilíngue."},
                          {"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            
            analise = json.loads(response.choices[0].message.content)
            
            art_completo = {**art, **analise}
            avaliados.append(art_completo)
            
        except Exception as e:
            print(f"Erro ao avaliar artigo {art['titulo']}: {e}")
            avaliados.append({**art, "nota": 0, "justificativa": "Erro na análise da IA."})
            
    return avaliados
#_________________________________________________________________________________________________________________________________________________