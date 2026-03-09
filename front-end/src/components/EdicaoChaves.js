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
      // 1. Enviamos TODOS os parâmetros para o Back-end (Performance e Filtro)
      const response = await axios.post(`${API_URL}/buscar-artigos`, {
        id_busca: dadosBusca.id_busca,
        string_pt: stringPt,
        string_en: stringEn,
        contexto_pt: contextoPt,
        contexto_en: contextoEn,
        
        // 2. NOVOS CAMPOS: Transportados do Questionário através do App.js
        ano_inicio: dadosBusca.anoInicio,
        limite_base: dadosBusca.limiteBase,
        bases: dadosBusca.bases
      });

      aoFinalizarBusca(response.data); 
    } catch (error) {
      console.error("Erro na busca:", error);
      alert("Erro na extração dos artigos. Verifique a conexão com o Back-end.");
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
        <input
          type="text"
          value={stringPt} 
          onChange={(e) => setStringPt(e.target.value)} 
          rows="3"
          placeholder="Preencher strings ou ajustar o escopo..."
        />
      </div>

      {/* BLOCO INTERNACIONAL (PubMed / arXiv) */}
      <div className="campo">
        <label>Strings de busca (Inglês):</label>
        <input 
          type="text"
          value={stringEn} 
          onChange={(e) => setStringEn(e.target.value)} 
          rows="3"
          placeholder="Preencher strings ou ajustar o escopo..."
        />
      </div>

      <div className="campo">
        <label>Contexto de Filtragem (IA):</label>
        <textarea 
          type="text"
          value={contextoPt} 
          onChange={(e) => setContextoPt(e.target.value)} 
          placeholder="Preencher contexto ou ajustar o escopo..."
          rows="3"
        />
      </div>

      <button onClick={handleBuscarArtigos} disabled={carregando}>
        {carregando ? "Extraindo e Filtrando Artigos (pode levar 1 min)..." : "Confirmar e Buscar Artigos"}
      </button>
    </div>
  );
};

export default EdicaoChaves;