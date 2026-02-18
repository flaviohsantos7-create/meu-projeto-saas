from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Definção do local do banco de dados
DATABASE_URL = "sqlite:///./projeto_saas.db"

Base = declarative_base()

class Busca(Base):
    """Tabela para armazenar o questionário e o contexto gerado pela IA"""
    __tablename__ = "buscas"

    id = Column(Integer, primary_key=True, index=True)
    tema = Column(String(255))
    problema = Column(Text)
    termos_obrigatorios = Column(Text)
    contexto_usuario = Column(Text)
    
    string_busca_pt = Column(Text)
    contexto_pt = Column(Text)

    string_busca_en = Column(Text)
    contexto_en = Column(Text)
    fonte = Column(Text)
    
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)

class Artigo(Base):
    """Tabela para armazenar os resultados filtrados"""
    __tablename__ = "artigos"

    id = Column(Integer, primary_key=True, index=True)
    busca_id = Column(Integer, ForeignKey("buscas.id"))

    string_busca_en = Column(Text)
    contexto_en = Column(Text)
    fonte = Column(Text)
    
    titulo = Column(String(500))
    resumo = Column(Text)
    autores = Column(String(500))
    data_publicacao = Column(String(100))
    
    # Resultado da Filtragem IA
    nota_compatibilidade = Column(Integer)
    justificativa_ia = Column(Text)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)