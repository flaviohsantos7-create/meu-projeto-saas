import requests

def buscar_crossref(query_pt, max_results=10, ano_limite=2020):
    url = "https://api.crossref.org/works"
    params = {
        "query": query_pt,
        "rows": max_results,
        # Inclusão do filtro from-pub-date dinâmico
        "filter": f"type:journal-article,from-pub-date:{ano_limite}",
        "select": "title,abstract,author,published,DOI"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    artigos = []
    for item in data['message']['items']:
        titulo = item.get('title', [''])[0]
        resumo = item.get('abstract', "Resumo não disponível na base Crossref.")
        
        resumo = resumo.replace('<jats:p>', '').replace('</jats:p>', '')

        autores = ", ".join([a.get('family', '') for a in item.get('author', [])])
        data_pub = str(item.get('published', {}).get('date-parts', [[0]])[0][0])
        doi = item.get('DOI')

        artigos.append({
            "titulo": titulo,
            "resumo": resumo,
            "autores": autores,
            "data": data_pub,
            "url": f"https://doi.org/{doi}" if doi else None,
            "fonte": "Crossref/SciELO"
        })
    return artigos