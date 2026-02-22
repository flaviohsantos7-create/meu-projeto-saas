import requests

def buscar_semantic_scholar(query_en, max_results=10):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query_en,
        "limit": max_results,
        "fields": "title,abstract,authors,year"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        artigos = []
        for item in data.get('data', []):
            artigos.append({
                "titulo": item.get('title'),
                "resumo": item.get('abstract') or "Resumo não disponível.",
                "autores": ", ".join([a['name'] for a in item.get('authors', [])]),
                "data": str(item.get('year', 'N/A')),
                "fonte": "Semantic Scholar"
            })
        return artigos
    except:
        return []