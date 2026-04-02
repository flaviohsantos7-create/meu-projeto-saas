import requests
import urllib.parse 

def buscar_doaj(query_pt, max_results=10, ano_limite=2020):
    query_completa = f"{query_pt} AND bibjson.year:[{ano_limite} TO 2030]"
    query_completa = query_completa.replace("'", '"')
    
    query_codificada = urllib.parse.quote(query_completa)
    url = f"https://doaj.org/api/v2/search/articles/{query_codificada}?pageSize={max_results}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        artigos = []

        for item in data.get('results', []):
            bibjson = item.get('bibjson', {})
            
            # CORREÇÃO DA EXTRAÇÃO DA URL
            link_direto = None
            links = bibjson.get('link', [])
            if isinstance(links, list):
                for l in links:
                    if isinstance(l, dict) and 'url' in l:
                        link_direto = l.get('url')
                        # Se achou o link de texto completo, é o ideal, então para o loop
                        if l.get('type') == 'fulltext':
                            break

            artigos.append({
                "titulo": bibjson.get('title'),
                "resumo": bibjson.get('abstract') or "Resumo não disponível.",
                "autores": ", ".join([a.get('name', '') for a in bibjson.get('author', [])]),
                "data": bibjson.get('year', 'N/A'),
                "url": link_direto,
                "fonte": "DOAJ"
            })
        return artigos
    except Exception as e:
        print(f"Erro no DOAJ: {e}")
        return []
