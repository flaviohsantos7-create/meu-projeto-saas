import requests

def buscar_doaj(query_pt, max_results=10):
    # Filtramos por idioma português (PT)
    url = f"https://doaj.org/api/v2/search/articles/{query_pt}?pageSize={max_results}&refine=language:Portuguese"
    try:
        response = requests.get(url)
        data = response.json()
        artigos = []
        for item in data.get('results', []):
            bibjson = item.get('bibjson', {})
            artigos.append({
                "titulo": bibjson.get('title'),
                "resumo": bibjson.get('abstract') or "Resumo não disponível.",
                "autores": ", ".join([a.get('name', '') for a in bibjson.get('author', [])]),
                "data": bibjson.get('year', 'N/A'),
                "fonte": "DOAJ (Brasil/Portugal)"
            })
        return artigos
    except:
        return []