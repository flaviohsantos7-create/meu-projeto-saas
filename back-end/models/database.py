import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# Puxa a URL da nuvem (Render/Neon). Se não encontrar, usa o SQLite local de forma segura.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./projeto_saas.db")

# Proteção do SQLAlchemy: Ele exige 'postgresql://' em vez de 'postgres://' nas versões novas
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))
    email = Column(String(150), unique=True, index=True)
    senha_hash = Column(String(255))
    data_cadastro = Column(DateTime, default=datetime.datetime.utcnow)
    
    logs = relationship("UserLog", back_populates="usuario")

class UserLog(Base):
    __tablename__ = "user_logs"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    data_acesso = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String(50))
    plataforma = Column(String(50)) # Captura Ex: windows, macos, android
    navegador = Column(String(50))  # Captura Ex: chrome, firefox, safari
    
    usuario = relationship("Usuario", back_populates="logs")

class Busca(Base):
    __tablename__ = "buscas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # nullable=True para não quebrar buscas antigas
    tema = Column(Text) # <--- CORREÇÃO AQUI (Antes era String(255))
    problema = Column(Text)
    termos_obrigatorios = Column(Text)
    
    # SEPARAÇÃO: Contexto (Resumo) vs Cenário (Aplicação)
    contexto_usuario = Column(Text) 
    cenario_aplicacao = Column(Text) 
    
    ano_limite = Column(Integer, default=2020)
    limite_por_base = Column(Integer, default=10)
    bases_selecionadas = Column(Text)
    
    # GARANTIA: Campos para Inglês
    string_pt = Column(Text)
    contexto_pt = Column(Text)
    string_en = Column(Text)
    contexto_en = Column(Text)
    
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)

class Artigo(Base):
    __tablename__ = "artigos"
    id = Column(Integer, primary_key=True, index=True)
    busca_id = Column(Integer, ForeignKey("buscas.id"))
    titulo = Column(Text) # <--- PREVENÇÃO: Alterado de String(500) para Text (Alguns artigos tem títulos imensos)
    resumo = Column(Text)
    autores = Column(Text) # <--- PREVENÇÃO: Alterado de String(500) para Text
    data_publicacao = Column(String(100))
    fonte = Column(String(100))
    url = Column(Text)
    nota_compatibilidade = Column(Integer)
    justificativa_ia = Column(Text)

# O SQLite exige o 'check_same_thread', o PostgreSQL não. Fazemos a separação automática.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # pool_pre_ping=True e pool_recycle=300 garantem que o Python reconecte
    # automaticamente caso o banco do Neon tenha fechado a conexão por inatividade.
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # --- AUTO-MIGRATOR (CORREÇÃO DO NEON) ---
    # Força o banco de dados na nuvem a converter as colunas e adicionar campos novos.
    if "postgres" in DATABASE_URL:
        try:
            with engine.begin() as conn: # engine.begin() faz o auto-commit de segurança
                conn.execute(text("ALTER TABLE buscas ALTER COLUMN tema TYPE TEXT;"))
                conn.execute(text("ALTER TABLE artigos ALTER COLUMN titulo TYPE TEXT;"))
                conn.execute(text("ALTER TABLE artigos ALTER COLUMN autores TYPE TEXT;"))
                conn.execute(text("ALTER TABLE buscas ADD COLUMN IF NOT EXISTS usuario_id INTEGER;"))
                conn.execute(text("ALTER TABLE user_logs ADD COLUMN IF NOT EXISTS plataforma VARCHAR(50);"))
                conn.execute(text("ALTER TABLE user_logs ADD COLUMN IF NOT EXISTS navegador VARCHAR(50);"))
        except Exception as e:
            pass # Ignora silenciosamente se as tabelas não existirem ou já estiverem corrigidas