from Bio import Entrez

Entrez.email = "flavio.h.santos7@aluno.senai.br"

def buscar_detalhes_pubmed(id_list):

    if not id_list:
        return []
        
    ids = ",".join(id_list)
    handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml")
    records = Entrez.read(handle)
    handle.close()
    
    artigos_extraidos = []
    for article in records['PubmedArticle']:
        try:
            titulo = article['MedlineCitation']['Article']['ArticleTitle']
            
            abstract_list = article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', ["Sem resumo disponível"])
            resumo = " ".join(abstract_list)
            
            autores_list = article['MedlineCitation']['Article'].get('AuthorList', [])
            nomes_autores = ", ".join([f"{a.get('LastName', '')} {a.get('Initials', '')}" for a in autores_list])
            data = article['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate'].get('Year', 'N/A')

            artigos_extraidos.append({
                "titulo": titulo,
                "resumo": resumo,
                "autores": nomes_autores,
                "data": data
            })
        except Exception as e:
            print(f"Erro ao processar um artigo: {e}")
            
    return artigos_extraidos

def executar_busca_completa(query, max_results=10):

    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()
    
    return buscar_detalhes_pubmed(record['IdList'])