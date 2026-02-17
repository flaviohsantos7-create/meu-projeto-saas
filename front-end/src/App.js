import React, { useState } from 'react';
import Questionario from './components/Questionario';
import EdicaoChaves from './components/EdicaoChaves';
import TabelaResultados from './components/TabelaResultados';
import './App.css';

function App() {
  const [etapa, setEtapa] = useState(1);
  
  const [dadosBusca, setDadosBusca] = useState({
    id_busca: null,
    string_busca: '',
    contexto: ''
  });

  const [artigosEncontrados, setArtigosEncontrados] = useState([]);

  const iniciarEdicao = (resultadoIA) => {
    setDadosBusca({
      id_busca: resultadoIA.id_busca,
      string_busca: resultadoIA.string_busca,
      contexto: resultadoIA.contexto
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
        {etapa === 1 && (
          <Questionario aoFinalizar={iniciarEdicao} />
        )}

        {etapa === 2 && (
          <EdicaoChaves 
            dadosBusca={dadosBusca} 
            aoFinalizarBusca={mostrarResultados} 
          />
        )}

        {etapa === 3 && (
          <TabelaResultados 
            artigos={artigosEncontrados} 
            aoVoltar={reiniciar} 
          />
        )}
      </main>
    </div>
  );
}

export default App;