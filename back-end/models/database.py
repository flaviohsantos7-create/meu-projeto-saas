from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./projeto_saas.db"
Base = declarative_base()

class Busca(Base):
    __tablename__ = "buscas"
    id = Column(Integer, primary_key=True, index=True)
    tema = Column(String(255))
    problema = Column(Text)
    termos_obrigatorios = Column(Text)
    
    # SEPARAÇÃO: Contexto (Resumo) vs Cenário (Aplicação)
    contexto_usuario = Column(Text) 
    cenario_aplicacao = Column(Text) #
    
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
    titulo = Column(String(500))
    resumo = Column(Text)
    autores = Column(String(500))
    data_publicacao = Column(String(100))
    fonte = Column(String(100))
    url = Column(Text)
    nota_compatibilidade = Column(Integer)
    justificativa_ia = Column(Text)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)