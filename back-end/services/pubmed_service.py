# from Bio import Entrez

# Entrez.email = "flavio.h.santos7@aluno.senai.br"

# def buscar_detalhes_pubmed(id_list):
#     if not id_list:
#         return []
        
#     ids = ",".join(id_list)
#     handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml")
#     records = Entrez.read(handle)
#     handle.close()
    
#     artigos_extraidos = []
#     for article in records['PubmedArticle']:
#         try:
#             titulo = article['MedlineCitation']['Article']['ArticleTitle']
            
#             # CORREÇÃO: Trata o problema do BioPython com listas vs strings
#             abstract_data = article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', ["Sem resumo disponível"])
#             if isinstance(abstract_data, list):
#                 resumo = " ".join([str(item) for item in abstract_data])
#             else:
#                 resumo = str(abstract_data) # Preserva o texto sem quebrar em letras
            
#             autores_list = article['MedlineCitation']['Article'].get('AuthorList', [])
#             nomes_autores = ", ".join([f"{a.get('LastName', '')} {a.get('Initials', '')}" for a in autores_list])
#             data = article['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate'].get('Year', 'N/A')

#             pmid = article.get('MedlineCitation', {}).get('PMID', {}).get('#text')

#             artigos_extraidos.append({
#                 "titulo": titulo,
#                 "resumo": resumo,
#                 "autores": nomes_autores,
#                 "data": data,
#                 "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
#                 "fonte": "PubMed" # Adicionado para a tag colorida funcionar
#             })
#         except Exception as e:
#             print(f"Erro ao processar um artigo: {e}")
            
#     return artigos_extraidos

# def executar_busca_completa(query, max_results=10, ano_limite=2020):
#     query_com_data = f'({query}) AND ("{ano_limite}/01/01"[Date - Publication] : "3000/12/31"[Date - Publication])'

#     try:
#         handle = Entrez.esearch(db="pubmed", term=query_com_data, retmax=max_results)
#         record = Entrez.read(handle)
#         handle.close()
        
#         return buscar_detalhes_pubmed(record['IdList'])
#     except Exception as e:
#         print(f"Erro na extração do PubMed: {e}")
#         return []

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
            
            # Trata o problema do BioPython com listas vs strings no resumo
            abstract_data = article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', ["Sem resumo disponível"])
            if isinstance(abstract_data, list):
                resumo = " ".join([str(item) for item in abstract_data])
            else:
                resumo = str(abstract_data) 
            
            autores_list = article['MedlineCitation']['Article'].get('AuthorList', [])
            nomes_autores = ", ".join([f"{a.get('LastName', '')} {a.get('Initials', '')}" for a in autores_list])
            data = article['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate'].get('Year', 'N/A')

            # CORREÇÃO DO ERRO STRINGELEMENT: Apenas convertemos o objeto direto para string
            pmid_obj = article.get('MedlineCitation', {}).get('PMID', '')
            pmid = str(pmid_obj) if pmid_obj else None

            artigos_extraidos.append({
                "titulo": titulo,
                "resumo": resumo,
                "autores": nomes_autores,
                "data": data,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
                "fonte": "PubMed" 
            })
        except Exception as e:
            print(f"Erro ao processar um artigo no PubMed: {e}")
            
    return artigos_extraidos

def executar_busca_completa(query, max_results=10, ano_limite=2020):
    query_com_data = f'({query}) AND ("{ano_limite}/01/01"[Date - Publication] : "3000/12/31"[Date - Publication])'

    try:
        handle = Entrez.esearch(db="pubmed", term=query_com_data, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        
        return buscar_detalhes_pubmed(record['IdList'])
    except Exception as e:
        print(f"Erro na extração do PubMed: {e}")
        return []