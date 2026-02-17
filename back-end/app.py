import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from services.pubmed_service import executar_busca_completa
from services.openai_service import filtrar_artigos_com_ia
from models.database import Artigo

from services.openai_service import gerar_chaves_e_contexto
from models.database import SessionLocal, init_db, Busca

app = Flask(__name__)
CORS(app)
load_dotenv()


init_db()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/gerar-contexto', methods=['POST'])
def rota_gerar_contexto():
    db = SessionLocal()
    try:
        dados = request.json
        
        resultado_ia = gerar_chaves_e_contexto(dados, client)
        
        nova_busca = Busca(
            tema=dados.get('tema'),
            problema=dados.get('problema'),
            termos_obrigatorios=dados.get('termos'),
            contexto_usuario=dados.get('contexto'),
            string_busca_gerada=resultado_ia.get('string_busca'),
            contexto_semantico=resultado_ia.get('contexto_semantico')
        )
        
        db.add(nova_busca)
        db.commit()
        db.refresh(nova_busca)

        return jsonify({
            "id_busca": nova_busca.id,
            "string_busca": nova_busca.string_busca_gerada,
            "contexto": nova_busca.contexto_semantico
        })

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route('/buscar-artigos', methods=['POST'])
def rota_buscar_artigos():
    db = SessionLocal()
    try:
        dados = request.json
        id_busca = dados.get('id_busca')
        string_busca = dados.get('string_busca')
        contexto = dados.get('contexto')

        resultados_brutos = executar_busca_completa(string_busca)

        resultados_filtrados = filtrar_artigos_com_ia(contexto, resultados_brutos, client)

        for art in resultados_filtrados:
            novo_artigo = Artigo(
                busca_id=id_busca,
                titulo=art['titulo'],
                resumo=art['resumo'],
                autores=art['autores'],
                data_publicacao=art['data'],
                nota_compatibilidade=art['nota'],
                justificativa_ia=art['justificativa']
            )
            db.add(novo_artigo)
        
        db.commit()

        return jsonify(resultados_filtrados)

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)