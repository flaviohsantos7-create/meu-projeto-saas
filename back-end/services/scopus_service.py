import os
import requests
from urllib.parse import quote

def buscar_scopus(query, max_results=10, ano_limite=2020):
    api_key = os.getenv("SCOPUS_API_KEY")
    scraper_key = os.getenv("SCRAPER_API_KEY")

    if not api_key:
        print("Aviso: SCOPUS_API_KEY não encontrada.")
        return []

    # VACINA: Garante aspas duplas e remove quebras de linha que podem vir da IA
    query_corrigida = query.replace("'", '"').replace("\n", " ").strip()
    
    url_elsevier = "https://api.elsevier.com/content/search/scopus"
    query_scopus = f"TITLE-ABS-KEY({query_corrigida}) AND PUBYEAR > {ano_limite - 1}"
    
    # Headers obrigatórios para a Scopus
    headers_scopus = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }

    try:
        if scraper_key:
            # ESTRATÉGIA DE ELITE: Usamos POST para o ScraperAPI. 
            # Isso permite enviar URLs gigantescas sem dar erro 500.
            proxy_url = "http://api.scraperapi.com"
            
            # O ScraperAPI recebe a URL alvo como um parâmetro de formulário no POST
            data_payload = {
                "api_key": scraper_key,
                "url": f"{url_elsevier}?query={quote(query_scopus)}&count={max_results}",
                "keep_headers": "true",
                "premium": "true"
            }
            
            print(f"Buscando Scopus via Túnel Proxy (Método Seguro para Queries Longas)...")
            # Aumentamos o timeout para 90s pois a Scopus é lenta em queries complexas
            response = requests.post(proxy_url, data=data_payload, headers=headers_scopus, timeout=90)
            
            if response.status_code != 200:
                print(f"Aviso: Túnel falhou com status {response.status_code}. Tentando alternativa direta...")
                response = requests.get(url_elsevier, headers=headers_scopus, params={"query": query_scopus, "count": max_results}, timeout=30)
        else:
            response = requests.get(url_elsevier, headers=headers_scopus, params={"query": query_scopus, "count": max_results}, timeout=30)

        response.raise_for_status()
        dados = response.json()
        
        artigos = []
        entradas = dados.get("search-results", {}).get("entry", [])
        
        # Se a Scopus retornar apenas um resultado, ela manda um objeto em vez de lista
        if isinstance(entradas, dict):
            entradas = [entradas]

        for item in entradas:
            if "error" in item or not item.get("dc:title") or item.get("dc:title") == "Result too large":
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
