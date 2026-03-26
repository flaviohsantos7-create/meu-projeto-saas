import requests

def buscar_openalex(query, max_results=10, ano_limite=2020):
    url = "https://api.openalex.org/works"
    
    # O OpenAlex busca no título, resumo e full-text automaticamente
    params = {
        "search": query,
        "filter": f"publication_year:>{ano_limite - 1}",
        "per-page": max_results,
        "mailto": "seu-email@gmail.com" # A API é livre, mas pede um e-mail para não bloquear por spam
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        dados = response.json()
        
        artigos = []
        for item in dados.get("results", []):
            titulo = item.get("title", "Título indisponível")
            if not titulo: continue
            
            # O OpenAlex envia o resumo criptografado (inverted index). Precisamos reconstruir:
            resumo = "Resumo não disponível."
            inverted = item.get("abstract_inverted_index")
            if inverted:
                # Descobre quantas palavras tem o texto
                tamanho = max([max(posicoes) for posicoes in inverted.values()]) + 1
                texto_resumo = [""] * tamanho
                for palavra, posicoes in inverted.items():
                    for pos in posicoes:
                        texto_resumo[pos] = palavra
                resumo = " ".join(texto_resumo)
                
            # Autores
            autores_list = [a.get("author", {}).get("display_name", "") for a in item.get("authorships", [])]
            autores = ", ".join(autores_list) if autores_list else "Autores não informados"
            
            data_pub = str(item.get("publication_year", "Data desconhecida"))
            link = item.get("doi") or item.get("id", "")
            
            artigos.append({
                "titulo": titulo,
                "resumo": resumo,
                "autores": autores,
                "data": data_pub,
                "fonte": "OpenAlex",
                "url": link
            })
        return artigos
    except Exception as e:
        print(f"Erro ao buscar no OpenAlex: {e}")
        return []