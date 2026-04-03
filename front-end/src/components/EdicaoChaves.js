import { API_URL } from '../api_config';
import React, { useState } from 'react';
import axios from 'axios';

const EdicaoChaves = ({ dadosBusca, aoFinalizarBusca, setGlobalLoading }) => {

  const [stringPt, setStringPt] = useState(dadosBusca.string_pt || '');
  const [stringEn, setStringEn] = useState(dadosBusca.string_en || '');
  const [contextoPt, setContextoPt] = useState(dadosBusca.contexto_pt || '');
  const [contextoEn, setContextoEn] = useState(dadosBusca.contexto_en || '');

  const [carregando, setCarregando] = useState(false);

  const autoResize = (e) => {
    e.target.style.height = 'auto';
    e.target.style.height = (e.target.scrollHeight) + 'px';
  };

  const handleBuscarArtigos = async () => {
    setCarregando(true);
    setGlobalLoading({ ativo: true, mensagem: "Extraindo e avaliando artigos (pode levar ~1-5 min)..." });
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
      setGlobalLoading({ ativo: false, mensagem: "" });
    }
  };

  return (
    <div className="container-chaves">
      <h2>Revisão da Estratégia de Busca</h2>
      <p>Você pode complementar ou retirar o que desejar antes da busca.</p>
      <p>Revise-as abaixo:</p>

      {/* BLOCO NACIONAL (Crossref / SciELO) */}
      <div className="campo">
        <label>Strings de busca (Português):</label>
        <textarea
          value={stringPt} 
          onChange={(e) => setStringPt(e.target.value)} 
          onInput={autoResize}
          rows="2"
          placeholder="..."
        />
      </div>

      {/* BLOCO INTERNACIONAL (PubMed / arXiv) */}
      <div className="campo">
        <label>Strings de busca (Inglês):</label>
        <textarea 
          value={stringEn} 
          onChange={(e) => setStringEn(e.target.value)} 
          onInput={autoResize}
          rows="2"
          placeholder="..."
        />
      </div>

      <div className="campo">
        <label>Contexto de Filtragem (IA):</label>
        <textarea 
          value={contextoPt} 
          onChange={(e) => setContextoPt(e.target.value)} 
          onInput={autoResize}
          placeholder="..."
          rows="4"
        />
      </div>

      <button onClick={handleBuscarArtigos} disabled={carregando}>
        {carregando ? "Agurde..." : "Confirmar e Buscar Artigos"}
      </button>
    </div>
  );
};

export default EdicaoChaves;
