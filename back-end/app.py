import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from services.pubmed_service import executar_busca_completa

from models.database import Artigo

from models.database import SessionLocal, init_db, Busca

from services.pubmed_service import executar_busca_completa as buscar_pubmed
from services.arxiv_service import buscar_arxiv
from services.crossref_service import buscar_crossref
from services.semantic_scholar_service import buscar_semantic_scholar
from services.doaj_service import buscar_doaj
from services.openai_service import gerar_estratégia_bilíngue, filtrar_artigos_ia_unificado

#___________________________________________________________________________________________________________________________________________________________
app = Flask(__name__)
CORS(app)
load_dotenv()

init_db()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#___________________________________________________________________________________________________________________________________________________________

@app.route('/gerar-contexto', methods=['POST'])
def rota_gerar_contexto():
    dados = request.json
    print(f"Dados recebidos: {dados}") 

    estrategia = gerar_estratégia_bilíngue(dados, client)
    
    db = SessionLocal()
    try:
        nova_busca = Busca(
            tema=dados.get('tema'),
            problema=dados.get('problema'),
            termos_obrigatorios=dados.get('termos'),

            contexto_usuario=dados.get('contexto_resumo'),
            cenario_aplicacao=dados.get('cenario'),

            ano_limite=int(dados.get('anoInicio', 2020)),
            limite_por_base=int(dados.get('limiteBase', 10)),
            bases_selecionadas=",".join(dados.get('bases', [])),

            string_pt=estrategia.get('string_pt'),
            contexto_pt=estrategia.get('contexto_pt'),
            string_en=estrategia.get('string_en'),
            contexto_en=estrategia.get('contexto_en')
        )
        
        db.add(nova_busca)
        db.commit()
        db.refresh(nova_busca)
        
        return jsonify({
            "id_busca": nova_busca.id,
            "string_pt": nova_busca.string_pt,
            "string_en": nova_busca.string_en,
            "contexto_pt": nova_busca.contexto_pt,
            "contexto_en": nova_busca.contexto_en,
            "ano_limite": nova_busca.ano_limite,
            "limite_por_base": nova_busca.limite_por_base
        })
    except Exception as e:
        db.rollback()
        print(f"Erro ao salvar busca: {e}")
        return jsonify({"error": "Erro interno ao processar estratégia"}), 500
    finally:
        db.close()
#____________________________________________________________________________________________________________________________________________________
@app.route('/buscar-artigos', methods=['POST'])
def rota_buscar_artigos():
    dados = request.json
    id_busca = dados.get('id_busca')
    s_en, s_pt = dados.get('string_en'), dados.get('string_pt')
    c_en, c_pt = dados.get('contexto_en'), dados.get('contexto_pt')
    ano_limite = dados.get('ano_inicio', 2020)
    bases_ativas = dados.get('bases', ['pubmed', 'arxiv', 'crossref', 'semantic', 'doaj'])

    artigos_brutos = []
    limite = int(dados.get('limite_base', 10))

    def busca_segura(func, query, nome):
        try:
            return func(query, max_results=limite) or []
        except Exception as e:
            print(f"Aviso: Falha na base {nome}: {e}")
            return []

    if 'pubmed' in bases_ativas:
        artigos_brutos += busca_segura(buscar_pubmed, dados.get('string_en'), "PubMed")

    if 'arxiv' in bases_ativas:
        artigos_brutos += busca_segura(buscar_arxiv, dados.get('string_en'), "arXiv")

    if 'crossref' in bases_ativas:
        artigos_brutos += busca_segura(buscar_crossref, dados.get('string_en'), "crossref")

    if 'semantic' in bases_ativas:
        artigos_brutos += busca_segura(buscar_semantic_scholar, dados.get('string_en'), "semantic")

    if 'doaj' in bases_ativas:
        artigos_brutos += busca_segura(buscar_doaj, dados.get('string_en'), "doaj")


    artigos_finalizados = filtrar_artigos_ia_unificado(
        dados.get('contexto_en'), dados.get('contexto_pt'), artigos_brutos, client
    )

    db = SessionLocal()
    for art in artigos_finalizados:
        novo = Artigo(
            busca_id=id_busca,
            titulo=art['titulo'],
            resumo=art['resumo'],
            autores=art.get('autores', 'N/A'),
            data_publicacao=art.get('data', 'N/A'),
            nota_compatibilidade=art.get('nota', 0),
            justificativa_ia=art.get('justificativa'),
            fonte=art.get('fonte'),
            url=art.get('url')
        )
        db.add(novo)
    db.commit()
    return jsonify(artigos_finalizados)
#____________________________________________________________________________________________________________________________________________________
if __name__ == '__main__':
    app.run(debug=True, port=5000)