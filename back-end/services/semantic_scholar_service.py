import requests

def buscar_semantic_scholar(query_en, max_results=10, ano_limite=2020):

    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    # LIMPEZA OBRIGATÓRIA: Remove operadores para a API não travar
    query_limpa = query_en.replace(" AND ", " ").replace(" OR ", " ").replace("(", "").replace(")", "").replace('"', '').replace("'", '"')
    
    # CORREÇÃO PARA O SEMANTIC SCHOLAR: API rejeita queries muito grandes.
    # Pegamos apenas as 5 primeiras palavras chave importantes para garantir resultados
    palavras = query_limpa.split()
    query_limpa = " ".join(palavras[:5])

    params = {
        "query": query_limpa,
        "limit": max_results,
        "fields": "title,abstract,authors,year,url", 
        "year": f"{ano_limite}-" 
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        artigos = []
        for item in data.get('data', []):
            artigos.append({
                "titulo": item.get('title'),
                "resumo": item.get('abstract') or "Resumo não disponível.",
                "autores": ", ".join([a['name'] for a in item.get('authors', [])]),
                "data": str(item.get('year', 'N/A')),
                "url": item.get('url'),
                "fonte": "Semantic Scholar"
            })
        return artigos
    except Exception as e:
        print(f"Erro no Semantic Scholar: {e}")
        return []
