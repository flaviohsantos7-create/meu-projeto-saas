import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Questionario from './components/Questionario';
import EdicaoChaves from './components/EdicaoChaves';
import TabelaResultados from './components/TabelaResultados';
import { API_URL } from './api_config'; 
import './App.css';
import Login from './components/Login';

// --- INJETOR DE TOKEN DE SEGURANÇA ---
// Isso garante que todas as requisições enviem o Token do usuário logado automaticamente
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function App() {

  const [etapa, setEtapa] = useState(1);
  const [sidebarAberta, setSidebarAberta] = useState(false); 
  const [historico, setHistorico] = useState([]); 
  
  const [globalLoading, setGlobalLoading] = useState({ ativo: false, mensagem: "" });

  const [modal, setModal] = useState({ tipo: null, id: null });
  const [inputRenomear, setInputRenomear] = useState("");

  const [formData, setFormData] = useState({
    tema: '', problema: '', termos: '', contexto_resumo: '', cenario: '',
    anoInicio: 2020, limiteBase: 10, bases: ['pubmed', 'arxiv', 'crossref', 'semantic', 'doaj', 'scopus', 'openalex']
  });

  const [dadosBusca, setDadosBusca] = useState({
    id_busca: null, string_pt: '', string_en: '', contexto_pt: '', contexto_en: ''
  });

  const [artigosEncontrados, setArtigosEncontrados] = useState([]);

  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('nomeUsuario');
    setIsAuthenticated(false);
    limparPesquisa();
  };

  // Rolar para o topo do CONTEÚDO PRINCIPAL sempre que a etapa mudar
  useEffect(() => {
    const mainContent = document.querySelector('.main-content-gemini');
    if (mainContent) {
      mainContent.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [etapa]);

  useEffect(() => {
    carregarHistorico();
  }, []);

  const carregarHistorico = async () => {
    try {
      const response = await axios.get(`${API_URL}/historico`); 
      const historicoFormatado = response.data.map(item => ({
        ...item, localNome: item.tema, oculto: false, fixado: false
      }));
      setHistorico(historicoFormatado);
    } catch (error) {
      console.error("Erro ao carregar histórico", error);
    }
  };

  const fecharModal = () => {
    setModal({ tipo: null, id: null });
    setInputRenomear("");
  };

  const handleExcluir = (id, e) => {
    e.stopPropagation();
    setModal({ tipo: 'excluir', id: id });
  };
  const confirmarExcluir = () => {
    setHistorico(hist => hist.map(h => h.id === modal.id ? { ...h, oculto: true } : h));
    fecharModal();
  };

  const handleRenomear = (id, e) => {
    e.stopPropagation();
    const item = historico.find(h => h.id === id);
    setInputRenomear(item ? item.localNome : "");
    setModal({ tipo: 'renomear', id: id });
  };
  const confirmarRenomear = () => {
    if (inputRenomear.trim() !== "") {
      setHistorico(hist => hist.map(h => h.id === modal.id ? { ...h, localNome: inputRenomear } : h));
    }
    fecharModal();
  };

  const handleFixar = (id, e) => {
    e.stopPropagation();
    setHistorico(hist => hist.map(h => h.id === id ? { ...h, fixado: !h.fixado } : h));
  };

  const handleCompartilhar = (e) => {
    e.stopPropagation();
    setModal({ tipo: 'compartilhar', id: null });
  };

  const carregarPesquisaAntiga = async (idBusca) => {
      try {
        setSidebarAberta(false); 
        setModal({ tipo: null, id: null }); // Fecha modal se estiver aberto
        
        // --- CORREÇÃO: Força a rolagem para o topo imediatamente ao clicar no card ---
        const mainContent = document.querySelector('.main-content-gemini');
        if (mainContent) {
          mainContent.scrollTo({ top: 0, behavior: 'smooth' });
        }
        // ----------------------------------------------------------------------------
        
        setFormData({
          tema: '', problema: '', termos: '', contexto_resumo: '', cenario: '',
          anoInicio: 2020, limiteBase: 10, bases: ['pubmed', 'arxiv', 'crossref', 'semantic', 'doaj', 'scopus', 'openalex']
        });
        setDadosBusca({
          id_busca: null, string_pt: '', string_en: '', contexto_pt: '', contexto_en: ''
        });
        
        const response = await axios.get(`${API_URL}/busca/${idBusca}/artigos`); 
        
        if (response.data && response.data.length > 0) {
          setArtigosEncontrados(response.data);
          setEtapa(3);
        } else {
          setModal({ tipo: 'alertaVazio', id: idBusca });
        }
      } catch (error) {
        console.error("Erro ao carregar pesquisa antiga:", error);
        alert("Houve um erro de conexão com o servidor.");
      }
    };

  const iniciarEdicao = (resultadoIA, dadosForm) => {
    setDadosBusca({
      id_busca: resultadoIA.id_busca, string_pt: resultadoIA.string_pt,
      string_en: resultadoIA.string_en, contexto_pt: resultadoIA.contexto_pt,
      contexto_en: resultadoIA.contexto_en, anoInicio: dadosForm.anoInicio,
      limiteBase: dadosForm.limiteBase, bases: dadosForm.bases
    });
    setEtapa(2);
    carregarHistorico(); 
  };

  const mostrarResultados = (artigos) => {
    setArtigosEncontrados(artigos);
    setEtapa(3);
  };

  const limparPesquisa = () => {
    setEtapa(1);
    setArtigosEncontrados([]);
    setFormData({
      tema: '', problema: '', termos: '', contexto_resumo: '', cenario: '',
      anoInicio: 2020, limiteBase: 10, bases: ['pubmed', 'arxiv', 'crossref', 'semantic', 'doaj', 'scopus', 'openalex']
    });
    setDadosBusca({
      id_busca: null, string_pt: '', string_en: '', contexto_pt: '', contexto_en: ''
    });
  };

  const reiniciar = () => {
    limparPesquisa();
  };

  const voltarEtapa = (novaEtapa) => {
    setEtapa(novaEtapa);
  };

  const historicoVisivel = historico
    .filter(h => !h.oculto)
    .sort((a, b) => Number(b.fixado) - Number(a.fixado));

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="app-wrapper">
      
      {/* BARRA LATERAL GEMINI */}
      <aside className={`sidebar-gemini ${sidebarAberta ? 'aberta' : 'fechada'}`}>
        <div style={{ marginBottom: '20px' }}>
          <button className="btn-hamburguer" onClick={() => setSidebarAberta(false)}>☰</button>
        </div>

        <h3 style={{ fontSize: '1em', color: '#202124', marginBottom: '15px' }}>Recentes</h3>
        
        {/* CONTAINER DO HISTÓRICO COM ROLAGEM PRÓPRIA */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '5px' }}>
          {historicoVisivel.length > 0 ? (
            historicoVisivel.map((item) => (
              <div key={item.id} className="historico-item" onClick={() => carregarPesquisaAntiga(item.id)}>
                <div className="historico-item-header">
                  <span className="historico-titulo">
                    {item.fixado && "📌 "} {item.localNome}
                  </span>
                </div>
                <span className="historico-data">{item.data}</span>
                
                <div className="historico-acoes">
                  <button className="btn-acao" onClick={(e) => handleFixar(item.id, e)} title="Fixar no Topo">📌</button>
                  <button className="btn-acao" onClick={(e) => handleRenomear(item.id, e)} title="Renomear">✏️</button>
                  <button className="btn-acao" onClick={(e) => handleCompartilhar(e)} title="Compartilhar">🔗</button>
                  <button className="btn-acao" onClick={(e) => handleExcluir(item.id, e)} title="Excluir" style={{color: '#d93025'}}>🗑️</button>
                </div>
              </div>
            ))
          ) : (
            <p style={{ fontSize: '0.85em', color: '#999', whiteSpace: 'normal' }}>Nenhuma pesquisa para exibir.</p>
          )}
        </div>

        <div className="container-sair">
          <button onClick={handleLogout} style={{ background: 'none', color: '#d93025', border: 'none', fontWeight: 'bold', cursor: 'pointer', fontSize: '0.95em', width: '100%', padding: '10px 0', margin: 0 }}>
            🚪 Sair do Sistema
          </button>
        </div>
      </aside>

      {/* CONTEÚDO PRINCIPAL */}
      <div className="main-content-gemini">
        {!sidebarAberta && (
          <button className="btn-hamburguer btn-hamburguer-fixo" onClick={() => setSidebarAberta(true)}>☰</button>
        )}

        <div className="app-container" style={{ paddingTop: !sidebarAberta ? '50px' : '0' }}>
          <header className="main-header">
            <h1>Buscador Acadêmico Inteligente</h1>
            <div className="progress-bar">
              <span className={etapa >= 1 ? "active" : ""} onClick={() => setEtapa(1)} style={{cursor: 'pointer'}}>1. Escopo</span>
              <span className={etapa >= 2 ? "active" : ""} onClick={() => setEtapa(2)} style={{cursor: 'pointer'}}>2. Estratégia</span>
              <span className={etapa >= 3 ? "active" : ""} onClick={() => setEtapa(3)} style={{cursor: 'pointer'}}>3. Resultados</span>
            </div>
          </header>

          <main className="content">
            {etapa === 1 && <Questionario aoFinalizar={iniciarEdicao} formData={formData} setFormData={setFormData} aoLimpar={limparPesquisa} setGlobalLoading={setGlobalLoading} />}
            {etapa === 2 && <EdicaoChaves dadosBusca={dadosBusca} aoFinalizarBusca={mostrarResultados} aoVoltar={() => voltarEtapa(1)} setGlobalLoading={setGlobalLoading} />}
            {etapa === 3 && <TabelaResultados artigos={artigosEncontrados} aoVoltar={reiniciar} />}
          </main>
        </div>
      </div>

      {/* RENDERIZAÇÃO DOS MODAIS CUSTOMIZADOS */}
      {modal.tipo && (
        <div className="modal-overlay" onClick={fecharModal}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            
            {modal.tipo === 'excluir' && (
              <>
                <h3>Confirmar Exclusão</h3>
                <p>Tem certeza que deseja remover esta pesquisa do seu histórico visual?</p>
                <div className="modal-botoes">
                  <button className="btn-cancelar" onClick={fecharModal}>Cancelar</button>
                  <button className="btn-perigo" onClick={confirmarExcluir}>Excluir</button>
                </div>
              </>
            )}

            {modal.tipo === 'renomear' && (
              <>
                <h3>Renomear Pesquisa</h3>
                <input
                  type="text"
                  value={inputRenomear}
                  onChange={(e) => setInputRenomear(e.target.value)}
                  autoFocus
                  onKeyDown={(e) => e.key === 'Enter' && confirmarRenomear()}
                />
                <div className="modal-botoes">
                  <button className="btn-cancelar" onClick={fecharModal}>Cancelar</button>
                  <button className="btn-confirmar" onClick={confirmarRenomear}>Salvar</button>
                </div>
              </>
            )}

            {modal.tipo === 'compartilhar' && (
              <>
                <h3>Compartilhar Pesquisa</h3>
                <p>Esta funcionalidade está em desenvolvimento e estará disponível em breve! 🚀</p>
                <div className="modal-botoes">
                  <button className="btn-confirmar" onClick={fecharModal}>Entendi</button>
                </div>
              </>
            )}

            {modal.tipo === 'alertaBackend' && (
              <>
                <h3>Carregar Tabela #{modal.id}</h3>
                <p>Para exibir a tabela antiga, precisamos criar a rota no Back-end (Python).</p>
                <div className="modal-botoes">
                  <button className="btn-confirmar" onClick={fecharModal}>Entendido</button>
                </div>
              </>
            )}

            {modal.tipo === 'alertaVazio' && (
              <>
                <h3>Pesquisa Vazia</h3>
                <p>Nenhum artigo foi salvo no banco de dados para esta pesquisa.</p>
                <div className="modal-botoes">
                  <button className="btn-confirmar" onClick={fecharModal}>Entendido</button>
                </div>
              </>
            )}

          </div>
        </div>
      )}

      {/* ADICIONE O MODAL DE LOADING AQUI */}
      {globalLoading.ativo && (
        <div className="modal-overlay">
          <div className="modal-loading-box">
            <div className="spinner"></div>
            <h3 style={{ margin: 0, color: '#2c3e50' }}>{globalLoading.mensagem}</h3>
            <p style={{ margin: '10px 0 0 0', fontSize: '0.9em', color: '#7f8c8d' }}>Por favor aguarde...</p>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;