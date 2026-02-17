import { API_URL } from '../api_config';
import React, { useState } from 'react';
import axios from 'axios';

const Questionario = ({ aoFinalizar }) => {
  const [formData, setFormData] = useState({
    tema: '',
    problema: '',
    termos: '',
    contexto: ''
  });

  const [carregando, setCarregando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCarregando(true);
    
    try {
      const response = await axios.post(`${API_URL}/gerar-contexto`, formData);
      
      aoFinalizar(response.data, formData); 
    } catch (error) {
      alert("Erro ao conectar com o servidor. Verifique se o Back-end está rodando.");
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="container">
      <h2>Início da Pesquisa Acadêmica</h2>
      <p>Responda às questões chaves para gerar suas strings de busca.</p>
      
      <form onSubmit={handleSubmit}>
        <label>Qual o tema central da pesquisa?</label>
        <input 
          type="text" 
          value={formData.tema} 
          onChange={(e) => setFormData({...formData, tema: e.target.value})} 
          required 
        />

        <label>Qual problema você está tentando resolver?</label>
        <textarea 
          value={formData.problema} 
          onChange={(e) => setFormData({...formData, problema: e.target.value})} 
          required 
        />

        <label>Termos ou Tecnologias Obrigatórias (Os termos devem ser separados por vígula): </label>
        <input 
          type="text" 
          value={formData.termos} 
          onChange={(e) => setFormData({...formData, termos: e.target.value})} 
        />

        <label>Contexto ou Cenário de Aplicação:</label>
        <textarea 
          value={formData.contexto} 
          onChange={(e) => setFormData({...formData, contexto: e.target.value})} 
        />

        <button type="submit" disabled={carregando}>
          {carregando ? "IA Processando..." : "Gerar Estratégia de Busca"}
        </button>
      </form>
    </div>
  );
};

export default Questionario;