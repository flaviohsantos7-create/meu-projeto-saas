import os
import requests

def buscar_scopus(query, max_results=10, ano_limite=2020):
    api_key = os.getenv("SCOPUS_API_KEY")
    if not api_key:
        print("Aviso: SCOPUS_API_KEY não encontrada no .env")
        return []

    url = "https://api.elsevier.com/content/search/scopus"
    
    # A Scopus exige o formato TITLE-ABS-KEY para buscar no título, resumo e palavras-chave
    query_scopus = f"TITLE-ABS-KEY({query}) AND PUBYEAR > {ano_limite - 1}"
    
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }
    
    params = {
        "query": query_scopus,
        "count": max_results
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        dados = response.json()
        
        artigos = []
        entradas = dados.get("search-results", {}).get("entry", [])
        
        for item in entradas:
            titulo = item.get("dc:title", "Título indisponível")
            # A API básica retorna o teaser do resumo no dc:description
            resumo = item.get("dc:description", "Resumo completo restrito pela camada gratuita da Scopus.")
            autores = item.get("dc:creator", "Autores não informados")
            data_pub_bruta = item.get("prism:coverDate", "Data desconhecida")
            data_pub = data_pub_bruta[:4] if data_pub_bruta != "Data desconhecida" else "Data desconhecida"
            
            # Pega o link oficial da Scopus
            links = item.get("link", [])
            link_oficial = next((l["@href"] for l in links if l.get("@ref") == "scopus"), "")
            
            artigos.append({
                "titulo": titulo,
                "resumo": resumo,
                "autores": autores,
                "data": data_pub,
                "fonte": "Scopus",
                "url": link_oficial
            })
            
        return artigos
    except Exception as e:
        print(f"Erro ao buscar na Scopus: {e}")
        return []