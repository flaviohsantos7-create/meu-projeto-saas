import { API_URL } from '../api_config';
import React, { useState } from 'react';
import axios from 'axios';

const Questionario = ({aoFinalizar, formData, setFormData, aoLimpar}) => {

  const [carregando, setCarregando] = useState(false);
  const [mostrarAvancado, setMostrarAvancado] = useState(false); 

  const handleBaseChange = (base) => {
    const novasBases = formData.bases.includes(base)
      ? formData.bases.filter(b => b !== base)
      : [...formData.bases, base];
    setFormData({ ...formData, bases: novasBases });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCarregando(true);
    try {
      const response = await axios.post(`${API_URL}/gerar-contexto`, formData);
      aoFinalizar(response.data, formData); 
    } catch (error) {
      alert("Erro ao conectar com o servidor.");
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="container">
      <h2>Início da Pesquisa Acadêmica</h2>
      <form onSubmit={handleSubmit}>
        <label>Qual o tema central da pesquisa?</label>
        <textarea rows="1" placeholder="..." value={formData.tema} onChange={(e) => setFormData({...formData, tema: e.target.value})} required />

        <label>Qual problema você está tentando resolver?</label>
        <textarea rows="1" placeholder="..." value={formData.problema} onChange={(e) => setFormData({...formData, problema: e.target.value})} required />

        <label style={{ marginTop: '20px' }}>Termos Obrigatórios (Separados por Vigula):</label>
        <textarea rows="1" placeholder="..." value={formData.termos} onChange={(e) => setFormData({...formData, termos: e.target.value})} />

        <label>Contexto do seu artigo (Resumo):</label>
        <textarea
          rows="3" 
          placeholder="..."
          value={formData.contexto_resumo}
          onChange={(e) => setFormData({...formData, contexto_resumo: e.target.value})} 
        />  
        
        <div style={{ marginTop: '20px', border: '1px solid #ddd', borderRadius: '8px', padding: '10px' }}>
          <div 
            onClick={() => setMostrarAvancado(!mostrarAvancado)} 
            style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
          >
            <strong style={{ color: '#3498db' }}>⚙️ Configurações Avançadas de Busca</strong>
            <span>{mostrarAvancado ? '▲' : '▼'}</span>
          </div>

          {mostrarAvancado && (
            <div className="secao-avancada" style={{ marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '15px' }}>
              <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
                <div style={{ flex: 1 }}>
                  <label>Desde o ano:</label>
                  <input type="number" placeholder="Ano..." value={formData.anoInicio} onChange={(e) => setFormData({...formData, anoInicio: e.target.value})} />
                </div>
                <div style={{ flex: 1 }}>
                  <label>Artigos por Base:</label>
                  <input type="range" min="5" max="30" step="5" value={formData.limiteBase} onChange={(e) => setFormData({...formData, limiteBase: e.target.value})} />
                  <div style={{ textAlign: 'center' }}>{formData.limiteBase} artigos</div>
                </div>
              </div>

              <label>Cenário de Aplicação:</label>
             <textarea rows="1" 
             value={formData.cenario}
             placeholder="Ex: Indústria, Hospital, Escola, Software..."
             onChange={(e) => setFormData({...formData, cenario: e.target.value})}
             />

              <label>Selecione as Bases de Dados:</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '10px' }}>
                {['pubmed', 'arxiv', 'crossref', 'semantic', 'doaj'].map(base => (
                  <div key={base} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input 
                      type="checkbox" 
                      checked={formData.bases.includes(base)} 
                      onChange={() => handleBaseChange(base)} 
                      style={{ width: 'auto', marginTop: 0 }}
                    />
                    <span style={{ fontSize: '0.9em', textTransform: 'capitalize' }}>
                      {base} {base === 'pubmed' ? '(Saúde)' : base === 'semantic' ? '(Geral)' : ''}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>  

        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          marginTop: '30px',
          width: '100%'
        }}>
          <button 
            type="button" 
            onClick={aoLimpar} 
            disabled={carregando} 
            style={{ 
              width: '228.8px', 
              height: '43.2px',
              backgroundColor: '#e74c3c', 
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: carregando ? 'not-allowed' : 'pointer',
              opacity: carregando ? 0.6 : 1,
              fontSize: '0.95em',
              fontWeight: '500',
              padding: 0 
            }}
          >
            Limpar Pesquisa
          </button>

          <button 
            type="submit" 
            disabled={carregando} 
            style={{ 
              width: '228.8px', 
              height: '43.2px',
              borderRadius: '4px',
              cursor: carregando ? 'not-allowed' : 'pointer',
              fontSize: '0.95em',
              fontWeight: '500',
              padding: 0 
            }}
          >
            {carregando ? "IA Processando..." : "Gerar Estratégia de Busca"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Questionario;