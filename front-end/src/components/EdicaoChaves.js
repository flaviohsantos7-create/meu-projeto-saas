import { API_URL } from '../api_config';
import React, { useState } from 'react';
import axios from 'axios';

const EdicaoChaves = ({ dadosBusca, aoFinalizarBusca }) => {
  const [stringBusca, setStringBusca] = useState(dadosBusca.string_busca);
  const [contexto, setContexto] = useState(dadosBusca.contexto);
  const [carregando, setCarregando] = useState(false);

  const handleBuscarArtigos = async () => {
    setCarregando(true);
    try {
      const response = await axios.post(`${API_URL}/gerar-contexto`, {
        id_busca: dadosBusca.id_busca,
        string_busca: stringBusca,
        contexto: contexto
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
      <p>Você pode complementar ou retirar o que desejar antes da busca.</p>

      <div className="campo">
        <label>String's de Busca:</label>
        <textarea 
          value={stringBusca} 
          onChange={(e) => setStringBusca(e.target.value)} 
          rows="4"
        />
      </div>

      <div className="campo">
        <label>Contexto Semântico para Filtragem:</label>
        <textarea 
          value={contexto} 
          onChange={(e) => setContexto(e.target.value)} 
          rows="4"
        />
      </div>

      <button onClick={handleBuscarArtigos} disabled={carregando}>
        {carregando ? "Extraindo e Filtrando Artigos..." : "Confirmar e Buscar Artigos"}
      </button>
    </div>
  );
};

export default EdicaoChaves;