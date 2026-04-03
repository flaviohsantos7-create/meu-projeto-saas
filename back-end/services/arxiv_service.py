import requests
import feedparser

def buscar_arxiv(query_en, max_results=10, ano_limite=2020):
    # Vacina de aspas
    query_en = query_en.replace("'", '"')
    
    url = "http://export.arxiv.org/api/query"
    
    query_com_data = f"{query_en} AND submittedDate:[{ano_limite}01010000 TO 202612312359]"
    
    params = {
        "search_query": f"all:{query_com_data}",
        "start": 0,
        "max_results": max_results
    }

    # Cabeçalho que simula um navegador real para evitar o Erro 429
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        print(f"Buscando no arXiv ({max_results} artigos)...")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 429:
            print("arXiv bloqueou temporariamente (429). Aguardando próximo ciclo.")
            return []

        response.raise_for_status()
        feed = feedparser.parse(response.content)
        
        artigos = []
        for entry in feed.entries:
            artigos.append({
                "titulo": entry.title,
                "resumo": entry.summary,
                "autores": ", ".join(author.name for author in entry.authors),
                "data": entry.published[:4],
                "url": entry.id,
                "fonte": "arXiv"
            })
        return artigos
    except Exception as e:
        print(f"Erro no arXiv: {e}")
        return []
