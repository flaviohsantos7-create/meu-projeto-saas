# import requests

# def buscar_doaj(query_pt, max_results=10, ano_limite=2000):
#     # Ponto 4: Inclusão do filtro de ano na query do DOAJ
#     query_completa = f"{query_pt} AND bibjson.year:>={ano_limite}"
#     url = f"https://doaj.org/api/v2/search/articles/{query_completa}?pageSize={max_results}"
    
#     try:
#         response = requests.get(url, timeout=10)
#         data = response.json()
#         artigos = []

#         for item in data.get('results', []):
#             bibjson = item.get('bibjson', {})
            
#             # Ponto 6: Extração robusta da URL (Evita o erro 'StringElement')
#             link_direto = None
#             links = bibjson.get('link', [])
#             if isinstance(links, list) and len(links) > 0:
#                 primeiro_link = links[0]
#                 # Verifica se é um dicionário antes de usar .get()
#                 if isinstance(primeiro_link, dict):
#                     link_direto = primeiro_link.get('content')
#                 else:
#                     link_direto = str(primeiro_link)

#             artigos.append({
#                 "titulo": bibjson.get('title'),
#                 "resumo": bibjson.get('abstract') or "Resumo não disponível.",
#                 "autores": ", ".join([a.get('name', '') for a in bibjson.get('author', [])]),
#                 "data": bibjson.get('year', 'N/A'),
#                 "url": link_direto,
#                 "fonte": "DOAJ"
#             })
#         return artigos
#     except Exception as e:
#         print(f"Erro no DOAJ: {e}")
#         return []

import requests

def buscar_doaj(query_pt, max_results=10, ano_limite=2020):
    # Inclusão do filtro de ano na query do DOAJ
    query_completa = f"{query_pt} AND bibjson.year:>={ano_limite}"
    url = f"https://doaj.org/api/v2/search/articles/{query_completa}?pageSize={max_results}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        artigos = []

        for item in data.get('results', []):
            bibjson = item.get('bibjson', {})
            
            link_direto = None
            links = bibjson.get('link', [])
            if isinstance(links, list) and len(links) > 0:
                primeiro_link = links[0]
                if isinstance(primeiro_link, dict):
                    link_direto = primeiro_link.get('content')
                else:
                    link_direto = str(primeiro_link)

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