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

    estrategia = gerar_estratégia_bilíngue(dados, client)
    
    db = SessionLocal()
  
    nova_busca = Busca(
        tema=dados.get('tema'),
        problema=dados.get('problema'),
        termos_obrigatorios=dados.get('termos'),
        contexto_usuario=dados.get('contexto'),
        string_busca_pt=estrategia['string_pt'],
        string_busca_en=estrategia['string_en'],
        contexto_pt=estrategia['contexto_pt'],
        contexto_en=estrategia['contexto_en']
    )
    db.add(nova_busca)
    db.commit()
    db.refresh(nova_busca)
    
    return jsonify({
        "id_busca": nova_busca.id,
        "string_pt": nova_busca.string_busca_pt,
        "string_en": nova_busca.string_busca_en,
        "contexto_pt": nova_busca.contexto_pt,
        "contexto_en": nova_busca.contexto_en
    })
#____________________________________________________________________________________________________________________________________________________
@app.route('/buscar-artigos', methods=['POST'])
def rota_buscar_artigos():
    dados = request.json
    id_busca = dados.get('id_busca')
    s_en = dados.get('string_en')
    s_pt = dados.get('string_pt')
    c_en = dados.get('contexto_en')
    c_pt = dados.get('contexto_pt')

    try:

        limite = 10

        res_pubmed = buscar_pubmed(s_en, max_results=limite) or []
        res_arxiv = buscar_arxiv(s_en, max_results=limite) or []
        res_semantic = buscar_semantic_scholar(s_en, max_results=limite) or []
        res_crossref = buscar_crossref(s_pt, max_results=limite) or []
        res_doaj = buscar_doaj(s_pt, max_results=limite) or []

        lista_bruta = res_pubmed + res_arxiv + res_semantic + res_crossref + res_doaj

        if not lista_bruta:
            return jsonify({"error": "Nenhum artigo encontrado nas bases."}), 404

        artigos_finalizados = filtrar_artigos_ia_unificado(
            c_en, c_pt, lista_bruta, client
        )

        db = SessionLocal()
        for art in artigos_finalizados:
            novo_artigo = Artigo(
                busca_id=id_busca,
                titulo=art['titulo'],
                resumo=art['resumo'],
                autores=art.get('autores', 'N/A'),
                data_publicacao=art.get('data', 'N/A'),
                nota_compatibilidade=art['nota'],
                justificativa_ia=art['justificativa'],
                fonte=art.get('fonte', 'Desconhecida')
            )
            db.add(novo_artigo)
        db.commit()
        
        return jsonify(artigos_finalizados)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#____________________________________________________________________________________________________________________________________________________
if __name__ == '__main__':
    app.run(debug=True, port=5000)