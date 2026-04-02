import os
import concurrent.futures
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import Usuario, UserLog
import datetime

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
from services.scopus_service import buscar_scopus
from services.openalex_service import buscar_openalex

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#___________________________________________________________________________________________________________________________________________________________
app = Flask(__name__)
CORS(app)
load_dotenv()

init_db()
#___________________________________________________________________________________________________________________________________________________________
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#___________________________________________________________________________________________________________________________________________________________
# Configuração de Segurança JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "chave-secreta-provisoria-mudar-em-producao")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=7) # O login dura 7 dias
jwt = JWTManager(app)
#___________________________________________________________________________________________________________________________________________________________
# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    dados = request.json
    db = SessionLocal()
    try:
        if db.query(Usuario).filter(Usuario.email == dados.get('email')).first():
            return jsonify({"error": "E-mail já cadastrado"}), 400
            
        novo_usuario = Usuario(
            nome=dados.get('nome'),
            email=dados.get('email'),
            senha_hash=generate_password_hash(dados.get('senha')) # Criptografa a senha
        )
        db.add(novo_usuario)
        db.commit()
        return jsonify({"message": "Usuário criado com sucesso!"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
#___________________________________________________________________________________________________________________________________________________________
@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == dados.get('email')).first()
        
        if not usuario or not check_password_hash(usuario.senha_hash, dados.get('senha')):
            return jsonify({"error": "E-mail ou senha incorretos"}), 401
            
        # Registra o Log de Acesso
        novo_log = UserLog(
            usuario_id=usuario.id, 
            ip_address=request.remote_addr,
            plataforma=request.user_agent.platform,
            navegador=request.user_agent.browser
        )
        db.add(novo_log)
        db.commit()
        
        # Gera o Token JWT
        token_acesso = create_access_token(identity=str(usuario.id))
        return jsonify({"access_token": token_acesso, "nome": usuario.nome}), 200
    except Exception as e:
        return jsonify({"error": "Erro no servidor"}), 500
    finally:
        db.close()
#___________________________________________________________________________________________________________________________________________________________
@app.route('/google-login', methods=['POST'])
def google_login():
    token = request.json.get('token')
    try:
        # Pega a chave do Google no seu .env
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        
        # Verifica com os servidores do Google se o token é legítimo
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
        
        email = idinfo['email']
        nome = idinfo.get('name', 'Usuário Google')
        
        db = SessionLocal()
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        # Se for o primeiro acesso, cria a conta silenciosamente
        if not usuario:
            usuario = Usuario(
                nome=nome,
                email=email,
                senha_hash=generate_password_hash(os.urandom(24).hex()) # Senha aleatória gigante
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
            
        # Registra o Log
        novo_log = UserLog(
            usuario_id=usuario.id, 
            ip_address=request.remote_addr,
            plataforma=request.user_agent.platform,
            navegador=request.user_agent.browser
        )
        db.add(novo_log)
        db.commit()
        
        # Gera o nosso JWT para manter o padrão
        token_acesso = create_access_token(identity=str(usuario.id))
        return jsonify({"access_token": token_acesso, "nome": usuario.nome}), 200
        
    except ValueError:
        return jsonify({"error": "Token do Google inválido ou expirado"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

#___________________________________________________________________________________________________________________________________________________________
@app.route('/esqueci-senha', methods=['POST'])
def esqueci_senha():
    email_usuario = request.json.get('email')
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email_usuario).first()
        if not usuario:
            # Por segurança, sempre dizemos que enviamos para não vazar quais e-mails existem no banco
            return jsonify({"message": "Se o e-mail existir, um link de recuperação foi enviado."}), 200
        
        # Gera um Token que expira em exatos 15 minutos
        reset_token = create_access_token(identity=str(usuario.id), expires_delta=datetime.timedelta(minutes=15))

        url_front = os.getenv("FRONTEND_URL", "https://meu-projeto-frontend-saas.onrender.com")
        link_reset = f"{url_front}/?reset={reset_token}"
        
        # Monta o E-mail
        remetente = os.getenv("EMAIL_REMETENTE")
        senha_app = os.getenv("EMAIL_SENHA_APP")
        
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = email_usuario
        msg['Subject'] = "Recuperação de Senha - Buscador SaaS"
        corpo = f"Olá {usuario.nome},\n\nVocê solicitou a recuperação de senha. Clique no link abaixo para criar uma nova (válido por 15 minutos):\n\n{link_reset}\n\nSe você não solicitou isso, pode ignorar este e-mail em segurança."
        msg.attach(MIMEText(corpo, 'plain'))
        
        # Envia o E-mail usando o servidor do Google
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha_app)
        server.send_message(msg)
        server.quit()
        
        return jsonify({"message": "Link de recuperação enviado com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return jsonify({"error": "Falha técnica ao enviar e-mail."}), 500
    finally:
        db.close()
#___________________________________________________________________________________________________________________________________________________________
@app.route('/reset-senha', methods=['POST'])
def reset_senha():
    dados = request.json
    token = dados.get('token')
    nova_senha = dados.get('senha')
    db = SessionLocal()
    try:
        # Tenta decodificar o token. Se passou de 15 min, isso aqui falha e vai pro except
        decoded_token = decode_token(token)
        usuario_id = decoded_token['sub']
        
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            return jsonify({"error": "Usuário não encontrado."}), 404
            
        # Salva a nova senha criptografada
        usuario.senha_hash = generate_password_hash(nova_senha)
        db.commit()
        return jsonify({"message": "Sua senha foi atualizada com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": "O link é inválido ou já expirou (15 minutos)."}), 401
    finally:
        db.close()
#___________________________________________________________________________________________________________________________________________________________
@app.route('/gerar-contexto', methods=['POST'])
@jwt_required()
def rota_gerar_contexto():
    
    dados = request.json
    print(f"Dados recebidos: {dados}") 

    estrategia = gerar_estratégia_bilíngue(dados, client)
    
    db = SessionLocal()
    try:
        nova_busca = Busca(
            usuario_id=get_jwt_identity(),
            tema=estrategia.get('titulo_historico', dados.get('tema')),
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
@jwt_required()
def rota_buscar_artigos():
    dados = request.json
    id_busca = dados.get('id_busca')
    s_en, s_pt = dados.get('string_en'), dados.get('string_pt')
    c_en, c_pt = dados.get('contexto_en'), dados.get('contexto_pt')

    # BUSCA O TEMA NO BANCO DE DADOS PARA AJUDAR A IA
    tema_pesquisa = "Tema não informado"
    if id_busca:
        db = SessionLocal()
        busca_obj = db.query(Busca).filter(Busca.id == id_busca).first()
        if busca_obj and busca_obj.tema:
            tema_pesquisa = busca_obj.tema
        db.close()
    
    try:
        ano_limite = int(dados.get('anoInicio', 2020))
    except (ValueError, TypeError):
            ano_limite = 2020

    bases_ativas = dados.get('bases', ['pubmed', 'arxiv', 'crossref', 'semantic', 'doaj'])

    artigos_brutos = []
    limite = int(dados.get('limite_base', 10))

    def busca_segura(func, query, nome, ano):
        try:
            return func(query, max_results=limite, ano_limite=ano) or []
        except Exception as e:
            print(f"Aviso: Falha na base {nome}: {e}")
            return []

    # --- INÍCIO DA BUSCA PARALELA (MULTITHREADING) ---
    tarefas = []
    
    # O ThreadPoolExecutor vai disparar todas as APIs simultaneamente
    with concurrent.futures.ThreadPoolExecutor() as executor:
        if 'pubmed' in bases_ativas:
            tarefas.append(executor.submit(busca_segura, buscar_pubmed, s_en, "PubMed", ano_limite))
        if 'arxiv' in bases_ativas:
            tarefas.append(executor.submit(busca_segura, buscar_arxiv, s_en, "arXiv", ano_limite))
        if 'crossref' in bases_ativas:
            tarefas.append(executor.submit(busca_segura, buscar_crossref, s_en, "crossref", ano_limite))
        if 'semantic' in bases_ativas:
            tarefas.append(executor.submit(busca_segura, buscar_semantic_scholar, s_en, "semantic", ano_limite))
        if 'doaj' in bases_ativas:
            tarefas.append(executor.submit(busca_segura, buscar_doaj, s_en, "doaj", ano_limite))
        if 'scopus' in bases_ativas:
            tarefas.append(executor.submit(busca_segura, buscar_scopus, s_en, "Scopus", ano_limite))
        if 'openalex' in bases_ativas:
            tarefas.append(executor.submit(busca_segura, buscar_openalex, s_en, "OpenAlex", ano_limite))
        
        # À medida que cada API responde (independentemente da ordem), os artigos são adicionados
        for futuro in concurrent.futures.as_completed(tarefas):
            artigos_brutos.extend(futuro.result())
    # --- FIM DA BUSCA PARALELA ---

    artigos_finalizados = filtrar_artigos_ia_unificado(
        tema_pesquisa, c_en, c_pt, artigos_brutos, client
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
@jwt_required()
def rota_historico():
    usuario_id = get_jwt_identity()
    db = SessionLocal()
    try:
        buscas = db.query(Busca).filter(Busca.usuario_id == usuario_id).order_by(Busca.id.desc()).limit(15).all()
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
@jwt_required()
def rota_obter_artigos_antigos(id_busca):
    db = SessionLocal()
    try:
        # Busca no banco todos os artigos que pertencem a esta ID de busca
        artigos_salvos = db.query(Artigo).filter(Artigo.busca_id == id_busca).all()
        
        resultado = []
        for art in artigos_salvos:
            resultado.append({
                "titulo": art.titulo,
                "autores": art.autores,
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
