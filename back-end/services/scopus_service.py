import os
import requests

def buscar_scopus(query, max_results=10, ano_limite=2020):
    api_key = os.getenv("SCOPUS_API_KEY")
    scraper_key = os.getenv("SCRAPER_API_KEY")

    if not api_key:
        print("Erro: SCOPUS_API_KEY ausente.")
        return []

    # Tratamento rigoroso da query
    query_limpa = query.replace("'", '"').replace("\n", " ").strip()
    query_scopus = f"TITLE-ABS-KEY({query_limpa}) AND PUBYEAR > {ano_limite - 1}"
    
    # URL Alvo sem parâmetros de autenticação (segurança máxima)
    url_alvo = "https://api.elsevier.com/content/search/scopus"
    params_elsevier = {
        "query": query_scopus,
        "count": min(max_results, 25) # Algumas chaves Scopus limitam a 25 por página
    }

    # HEADERS: O segredo para evitar o erro 403
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        if scraper_key:
            # Preparamos a URL final para o ScraperAPI sem codificação dupla
            # O requests.Request().prepare() gera a URL perfeita
            req = requests.Request('GET', url_alvo, params=params_elsevier).prepare()
            
            payload_proxy = {
                'api_key': scraper_key,
                'url': req.url,
                'keep_headers': 'true', # CRÍTICO: Mantém o X-ELS-APIKey no túnel
                'premium': 'true'
            }
            
            print("Iniciando busca Scopus via Túnel Premium com Headers preservados...")
            response = requests.get("http://api.scraperapi.com", params=payload_proxy, headers=headers, timeout=60)
        else:
            response = requests.get(url_alvo, params=params_elsevier, headers=headers, timeout=30)

        if response.status_code == 403:
            print("Erro 403: A chave da Scopus foi rejeitada ou o limite de resultados foi excedido.")
            return []

        response.raise_for_status()
        dados = response.json()
        
        entradas = dados.get("search-results", {}).get("entry", [])
        if isinstance(entradas, dict): entradas = [entradas]

        artigos = []
        for item in entradas:
            if "error" in item or not item.get("dc:title"): continue
            
            artigos.append({
                "titulo": item.get("dc:title", "Título indisponível"),
                "resumo": item.get("dc:description", "Resumo restrito."),
                "autores": item.get("dc:creator", "N/A"),
                "data": (item.get("prism:coverDate", "0000"))[:4],
                "fonte": "Scopus",
                "url": next((l["@href"] for l in item.get("link", []) if l.get("@ref") == "scopus"), "")
            })
        return artigos

    except Exception as e:
        print(f"Falha na Scopus: {e}")
        return []
