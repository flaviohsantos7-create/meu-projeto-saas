import os
import requests
from urllib.parse import urlencode, quote

def buscar_scopus(query, max_results=10, ano_limite=2020):
    api_key = os.getenv("SCOPUS_API_KEY")
    scraper_key = os.getenv("SCRAPER_API_KEY") # A nossa nova chave do túnel

    if not api_key:
        print("Aviso: SCOPUS_API_KEY não encontrada.")
        return []

    url_elsevier = "https://api.elsevier.com/content/search/scopus"
    query_scopus = f"TITLE-ABS-KEY({query}) AND PUBYEAR > {ano_limite - 1}"
    
    params = {
        "query": query_scopus,
        "count": max_results
    }
    
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }
    
    try:
        if scraper_key:
            # 1. Monta a URL "crua" (sem codificar). 
            url_alvo_crua = f"{url_elsevier}?query={query_scopus}&count={max_results}"
            
            # 2. O 'requests' fará a codificação UMA ÚNICA VEZ ao montar os params do proxy
            payload_proxy = {
                'api_key': scraper_key,
                'url': url_alvo_crua, 
                'keep_headers': 'true',
                'premium': 'true'
            }
            print("Buscando Scopus via Túnel Proxy Premium (Codificação Perfeita)...")
            response = requests.get("http://api.scraperapi.com", params=payload_proxy, headers=headers, timeout=50)
        else:
            # Se não tiver chave do túnel (ex: rodando no PC da faculdade), vai direto
            print("Buscando Scopus via conexão direta...")
            response = requests.get(url_elsevier, headers=headers, params=params, timeout=20)
            
        response.raise_for_status()
        dados = response.json()
        
        artigos = []
        entradas = dados.get("search-results", {}).get("entry", [])
        
        for item in entradas:
            if "error" in item or not item.get("dc:title"):
                continue
            titulo = item.get("dc:title", "Título indisponível")
            resumo = item.get("dc:description", "Resumo completo restrito pela camada gratuita da Scopus.")
            autores = item.get("dc:creator", "Autores não informados")
            
            data_pub_bruta = item.get("prism:coverDate", "Data desconhecida")
            data_pub = data_pub_bruta[:4] if data_pub_bruta != "Data desconhecida" else "Data desconhecida"
            
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
