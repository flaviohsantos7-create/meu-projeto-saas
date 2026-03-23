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
    
    # Captura o ano escolhido no front-end
    ano_limite = dados.get('ano_inicio', 2020)
    bases_ativas = dados.get('bases', ['pubmed', 'arxiv', 'crossref', 'semantic', 'doaj'])

    artigos_brutos = []
    limite = int(dados.get('limite_base', 10))

    # MODIFICAÇÃO 1: Adicionamos o parâmetro 'ano' na função de segurança
    def busca_segura(func, query, nome, ano):
        try:
            # Passamos o ano_limite explicitamente para o serviço
            return func(query, max_results=limite, ano_limite=ano) or []
        except Exception as e:
            print(f"Aviso: Falha na base {nome}: {e}")
            return []

    # MODIFICAÇÃO 2: Repassamos a variável 'ano_limite' em todas as chamadas
    if 'pubmed' in bases_ativas:
        artigos_brutos += busca_segura(buscar_pubmed, s_en, "PubMed", ano_limite)

    if 'arxiv' in bases_ativas:
        artigos_brutos += busca_segura(buscar_arxiv, s_en, "arXiv", ano_limite)

    if 'crossref' in bases_ativas:
        artigos_brutos += busca_segura(buscar_crossref, s_en, "crossref", ano_limite)

    if 'semantic' in bases_ativas:
        artigos_brutos += busca_segura(buscar_semantic_scholar, s_en, "semantic", ano_limite)

    if 'doaj' in bases_ativas:
        artigos_brutos += busca_segura(buscar_doaj, s_en, "doaj", ano_limite)

    artigos_finalizados = filtrar_artigos_ia_unificado(
        c_en, c_pt, artigos_brutos, client
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
@app.route('/historico', methods=['GET'])
def rota_historico():
    db = SessionLocal()
    try:
        buscas = db.query(Busca).order_by(Busca.id.desc()).limit(10).all()
        resultado = []
        for b in buscas:
            resultado.append({
                "id": b.id,
                "tema": b.tema or "Sem tema",
                "data": b.data_criacao.strftime("%d/%m/%Y") if b.data_criacao else ""
            })
        return jsonify(resultado)
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return jsonify([])
    finally:
        db.close()
#____________________________________________________________________________________________________________________________________________________
@app.route('/busca/<int:id_busca>/artigos', methods=['GET'])
def rota_obter_artigos_antigos(id_busca):
    db = SessionLocal()
    try:
        # Busca no banco todos os artigos que pertencem a esta ID de busca
        artigos_salvos = db.query(Artigo).filter(Artigo.busca_id == id_busca).all()
        
        resultado = []
        for art in artigos_salvos:
            resultado.append({
                "titulo": art.titulo,
                "resumo": art.resumo,
                "data": art.data_publicacao,
                "nota": art.nota_compatibilidade,
                "justificativa": art.justificativa_ia,
                "fonte": art.fonte,
                "url": art.url
            })
            
        return jsonify(resultado)
    except Exception as e:
        print(f"Erro ao resgatar artigos da pesquisa {id_busca}: {e}")
        return jsonify({"error": "Erro ao carregar artigos antigos"}), 500
    finally:
        db.close()
#____________________________________________________________________________________________________________________________________________________
if __name__ == '__main__':
    app.run(debug=True, port=5000)