import urllib, urllib.request
import feedparser

def buscar_arxiv(query_en, max_results=10):
    base_url = 'http://export.arxiv.org/api/query?'
    query_url = f"search_query=all:{urllib.parse.quote(query_en)}&start=0&max_results={max_results}"
    
    response = urllib.request.urlopen(base_url + query_url).read()
    feed = feedparser.parse(response)
    
    artigos = []
    for entry in feed.entries:
        artigos.append({
            "titulo": entry.title,
            "resumo": entry.summary,
            "autores": ", ".join(author.name for author in entry.authors),
            "data": entry.published[:4],
            "fonte": "arXiv"
        })
    return artigos