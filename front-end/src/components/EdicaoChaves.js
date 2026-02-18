import { API_URL } from '../api_config';
import React, { useState } from 'react';
import axios from 'axios';

const EdicaoChaves = ({ dadosBusca, aoFinalizarBusca }) => {

  const [stringPt, setStringPt] = useState(dadosBusca.string_pt || '');
  const [stringEn, setStringEn] = useState(dadosBusca.string_en || '');
  const [contextoPt, setContextoPt] = useState(dadosBusca.contexto_pt || '');
  const [contextoEn, setContextoEn] = useState(dadosBusca.contexto_en || '');

  const [carregando, setCarregando] = useState(false);

  const handleBuscarArtigos = async () => {
    setCarregando(true);
    try {

      const response = await axios.post(`${API_URL}/buscar-artigos`, {
        id_busca: dadosBusca.id_busca,
        string_pt: stringPt,
        string_en: stringEn,
        contexto_pt: contextoPt,
        contexto_en: contextoEn
      });

      aoFinalizarBusca(response.data); 
    } catch (error) {
      alert("Erro na extração dos artigos. Verifique a conexão com as APIs.");
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="container-chaves">
      <h3>Revisão da Estratégia de Busca</h3>
      <p>Você pode complementar ou retirar o que desejar antes da busca. Revise-as abaixo:</p>

      {/* BLOCO NACIONAL (Crossref / SciELO) */}
      <div className="campo">
        <label>Strings de busca (Português):</label>
        <textarea 
          type="text"
          value={stringPt} 
          onChange={(e) => setStringPt(e.target.value)} 
          rows="3"
          placeholder="String para Crossref..."
        />
      </div>

      {/* BLOCO INTERNACIONAL (PubMed / arXiv) */}
      <div className="campo">
        <label>Strings de busca (Inglês):</label>
        <textarea 
          type="text"
          value={stringEn} 
          onChange={(e) => setStringEn(e.target.value)} 
          rows="3"
          placeholder="String para PubMed e arXiv..."
        />
      </div>

      <div className="campo">
        <label>Contexto de Filtragem (IA):</label>
        <textarea 
          type="text"
          value={contextoPt} 
          onChange={(e) => setContextoPt(e.target.value)} 
          rows="3"
        />
      </div>

      <button onClick={handleBuscarArtigos} disabled={carregando}>
        {carregando ? "Extraindo e Filtrando Artigos..." : "Confirmar e Buscar Artigos"}
      </button>
    </div>
  );
};

export default EdicaoChaves;