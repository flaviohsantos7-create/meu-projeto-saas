import React, { useState } from 'react';
import Questionario from './components/Questionario';
import EdicaoChaves from './components/EdicaoChaves';
import TabelaResultados from './components/TabelaResultados';
import './App.css';

function App() {
  const [etapa, setEtapa] = useState(1);
  
  // 1. Atualizamos o estado inicial para suportar os novos campos
  const [dadosBusca, setDadosBusca] = useState({
    id_busca: null,
    string_pt: '',
    string_en: '',
    contexto_pt: '',
    contexto_en: ''
  });

  const [artigosEncontrados, setArtigosEncontrados] = useState([]);

  // 2. CORREÇÃO CRÍTICA: Mapear os dados que vêm da IA para os novos nomes
  const iniciarEdicao = (resultadoIA) => {
    setDadosBusca({
      id_busca: resultadoIA.id_busca,
      string_pt: resultadoIA.string_pt,
      string_en: resultadoIA.string_en,
      contexto_pt: resultadoIA.contexto_pt,
      contexto_en: resultadoIA.contexto_en
    });
    setEtapa(2);
  };

  const mostrarResultados = (artigos) => {
    setArtigosEncontrados(artigos);
    setEtapa(3);
  };

  const reiniciar = () => {
    setEtapa(1);
    setArtigosEncontrados([]);
    setDadosBusca({ id_busca: null, string_pt: '', string_en: '', contexto_pt: '', contexto_en: '' });
  };

  return (
    <div className="app-container">
      <header className="main-header">
        <h1>Buscador Acadêmico Inteligente</h1>
        <div className="progress-bar">
          <span className={etapa >= 1 ? "active" : ""}>1. Escopo</span>
          <span className={etapa >= 2 ? "active" : ""}>2. Estratégia</span>
          <span className={etapa >= 3 ? "active" : ""}>3. Resultados</span>
        </div>
      </header>

      <main className="content">
        {etapa === 1 && <Questionario aoFinalizar={iniciarEdicao} />}
        {etapa === 2 && <EdicaoChaves dadosBusca={dadosBusca} aoFinalizarBusca={mostrarResultados} />}
        {etapa === 3 && <TabelaResultados artigos={artigosEncontrados} aoVoltar={reiniciar} />}
      </main>
    </div>
  );
}

export default App;