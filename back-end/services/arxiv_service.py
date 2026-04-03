import urllib, urllib.request
import urllib.parse
import feedparser

def buscar_arxiv(query_en, max_results=10, ano_limite=2020):
    
    # VACINA: Força aspas duplas no lugar de aspas simples para evitar erros de sintaxe
    query_en = query_en.replace("'", '"')
    
    base_url = 'http://export.arxiv.org/api/query?'
    
    # Inclusão do filtro de data (de 01/01/ano_limite até 31/12/2026)
    query_com_data = f"{query_en} AND submittedDate:[{ano_limite}01010000 TO 202612312359]"
    query_url = f"search_query=all:{urllib.parse.quote(query_com_data)}&start=0&max_results={max_results}"
    
    url_completa = base_url + query_url
    
    # CRACHÁ: Adiciona o User-Agent para o arXiv não dar Erro 429 (Too Many Requests)
    req = urllib.request.Request(
        url_completa, 
        headers={'User-Agent': 'Projeto_Universitario_SaaS/1.0 (mailto:estudante@universidade.edu)'}
    )
    
    try:
        # Agora abrimos a URL passando o "req" (que contém o crachá)
        response = urllib.request.urlopen(req).read()
        feed = feedparser.parse(response)
        
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
        print(f"Erro ao buscar no arXiv: {e}")
        return []
