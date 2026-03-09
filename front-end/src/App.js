import React, { useState } from 'react';
import Questionario from './components/Questionario';
import EdicaoChaves from './components/EdicaoChaves';
import TabelaResultados from './components/TabelaResultados';
import './App.css';

function App() {
  const [etapa, setEtapa] = useState(1);
  
// Centralizamos o estado do formulário aqui para garantir a persistência (Ponto 3)
  const [formData, setFormData] = useState({
    tema: '',
    problema: '',
    termos: '',
    contexto_resumo: '',
    cenario: '',
    anoInicio: 2020,
    limiteBase: 10,
    bases: ['pubmed', 'arxiv', 'crossref', 'semantic', 'doaj']
  });

  const [dadosBusca, setDadosBusca] = useState({
    id_busca: null,
    string_pt: '',
    string_en: '',
    contexto_pt: '',
    contexto_en: ''
  })

  const [artigosEncontrados, setArtigosEncontrados] = useState([]);

  // 2. Função atualizada para capturar os dados do formulário e da IA
  const iniciarEdicao = (resultadoIA, dadosForm) => {
    setDadosBusca({
      id_busca: resultadoIA.id_busca,
      string_pt: resultadoIA.string_pt,
      string_en: resultadoIA.string_en,
      contexto_pt: resultadoIA.contexto_pt,
      contexto_en: resultadoIA.contexto_en,
      // Preservamos o que o usuário escolheu no questionário
      anoInicio: dadosForm.anoInicio,
      limiteBase: dadosForm.limiteBase,
      bases: dadosForm.bases
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

  // Função para permitir voltar etapas (Requisito 5 da sua estratégia)
  const voltarEtapa = (novaEtapa) => {
    setEtapa(novaEtapa);
  };

  return (
    <div className="app-container">
      <header className="main-header">
        <h1>Buscador Acadêmico Inteligente</h1>
        <div className="progress-bar">
          <span className={etapa >= 1 ? "active" : ""} onClick={() => setEtapa(1)} style={{cursor: 'pointer'}}>1. Escopo</span>
          <span className={etapa >= 2 ? "active" : ""} onClick={() => setEtapa(2)} style={{cursor: 'pointer'}}>2. Estratégia</span>
          <span className={etapa >= 3 ? "active" : ""} onClick={() => setEtapa(3)} style={{cursor: 'pointer'}}>2. Resultados</span>
          {/* <span className={etapa === 3 ? "active" : ""}>3. Resultados</span> */}
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
            aoVoltar={() => voltarEtapa(1)}
          />
        )}

        {etapa === 3 && (
          <TabelaResultados 
            artigos={artigosEncontrados} 
            aoVoltar={() => voltarEtapa(2)} 
          />
        )}
      </main>
    </div>
  );
}

export default App;