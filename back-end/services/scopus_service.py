import os
import requests

def buscar_scopus(query, max_results=10, ano_limite=2020):
    api_key = os.getenv("SCOPUS_API_KEY")
    scraper_key = os.getenv("SCRAPER_API_KEY")

    if not api_key:
        print("Aviso: SCOPUS_API_KEY não encontrada.")
        return []

    # VACINA: Scopus não aceita aspas simples.
    query_corrigida = query.replace("'", '"')
    
    url_elsevier = "https://api.elsevier.com/content/search/scopus"
    # A URL crua, montada manualmente sem urlencode para o proxy não engasgar
    query_scopus = f"TITLE-ABS-KEY({query_corrigida}) AND PUBYEAR > {ano_limite - 1}"
    
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }

    try:
        if scraper_key:
            # 1. Monta a URL alvo completamente crua
            url_alvo_crua = f"{url_elsevier}?query={query_scopus}&count={max_results}"
            
            payload_proxy = {
                'api_key': scraper_key,
                'url': url_alvo_crua,
                'keep_headers': 'true',
                'premium': 'true'
            }
            
            print("Buscando Scopus via Túnel Proxy Premium (URL Crua)...")
            response = requests.get("http://api.scraperapi.com", params=payload_proxy, headers=headers, timeout=50)
            
            if response.status_code != 200:
                print(f"Aviso: Túnel falhou com status {response.status_code}. Tentando Scopus via conexão direta...")
                response = requests.get(url_elsevier, headers=headers, params={"query": query_scopus, "count": max_results}, timeout=20)
                
        else:
            print("Buscando Scopus via conexão direta...")
            response = requests.get(url_elsevier, headers=headers, params={"query": query_scopus, "count": max_results}, timeout=20)
            
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
