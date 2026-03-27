import React, { useState } from 'react';
import axios from 'axios';
import { API_URL } from '../api_config';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import './Login.css';

// --- ÍCONES SVG MINIMALISTAS (Estilo Linha, igual à imagem solicitada) ---
const IconeOlhoAberto = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.644C3.67 8.5 7.652 4.5 12 4.5c4.348 0 8.332 4 9.964 7.178.07.133.07.312 0 .444C20.332 15.5 16.348 19.5 12 19.5c-4.348 0-8.332-4-9.964-7.178z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const IconeOlhoFechado = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
  </svg>
);

const Login = ({ onLogin }) => {
  const urlParams = new URLSearchParams(window.location.search);
  const tokenResetURL = urlParams.get('reset');

  const [modo, setModo] = useState(tokenResetURL ? 'reset' : 'login');
  const [formData, setFormData] = useState({ nome: '', email: '', senha: '' });
  const [mensagem, setMensagem] = useState({ tipo: '', texto: '' });
  const [carregando, setCarregando] = useState(false);
  
  // Estado para alternar entre texto e senha
  const [mostrarSenha, setMostrarSenha] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });

    try {
      if (modo === 'registro') {
        await axios.post(`${API_URL}/registro`, formData);
        setMensagem({ tipo: 'sucesso', texto: 'Conta criada! Faça login para entrar.' });
        setModo('login');
      } else if (modo === 'esqueci') {
        await axios.post(`${API_URL}/esqueci-senha`, { email: formData.email });
        setMensagem({ tipo: 'sucesso', texto: 'Se o e-mail existir, um link foi enviado para sua caixa de entrada.' });
        setModo('login');
      } else if (modo === 'reset') {
        await axios.post(`${API_URL}/reset-senha`, { token: tokenResetURL, senha: formData.senha });
        setMensagem({ tipo: 'sucesso', texto: 'Senha atualizada! Você já pode fazer login.' });
        window.history.replaceState({}, document.title, "/"); 
        setModo('login');
      } else {
        const response = await axios.post(`${API_URL}/login`, { email: formData.email, senha: formData.senha });
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('nomeUsuario', response.data.nome);
        onLogin(); 
      }
    } catch (error) {
      setMensagem({ 
        tipo: 'erro', 
        texto: error.response?.data?.error || 'Erro de conexão com o servidor.' 
      });
    } finally {
      setCarregando(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    setCarregando(true);
    setMensagem({ tipo: '', texto: '' });
    try {
      const response = await axios.post(`${API_URL}/google-login`, { token: credentialResponse.credential });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('nomeUsuario', response.data.nome);
      onLogin();
    } catch (error) {
      setMensagem({ tipo: 'erro', texto: 'Falha ao autenticar com o Google.' });
    } finally {
      setCarregando(false);
    }
  };

  return (
    <GoogleOAuthProvider clientId="407881544393-3e2bqbpf4igguol8dceks3l28bu6cb2s.apps.googleusercontent.com">
      <div className="login-wrapper">
        <div className="login-card">
          <h2>
            {modo === 'registro' ? 'Criar Conta' : 
             modo === 'esqueci' ? 'Recuperar Senha' : 
             modo === 'reset' ? 'Nova Senha' : 'Bem-vindo ao Buscador Acadêmico Inteligente'}
          </h2>
          <p>
            {modo === 'registro' ? 'Cadastre-se para acessar o buscador' : 
             modo === 'esqueci' ? 'Digite seu e-mail para receber um link de acesso' : 
             modo === 'reset' ? 'Crie uma nova senha de segurança' : 'Faça login para acessar seu histórico de pesquisas acadêmicas'}
          </p>

          {mensagem.texto && (
            <div className={mensagem.tipo === 'erro' ? 'login-erro' : 'login-sucesso'}>
              {mensagem.texto}
            </div>
          )}

          <form className="login-form" onSubmit={handleSubmit}>
            {modo === 'registro' && (
              <>
                <label>Nome Completo</label>
                <input type="text" placeholder="Digite seu Nome Completo" value={formData.nome} onChange={(e) => setFormData({...formData, nome: e.target.value})} required />
              </>
            )}
            
            {(modo === 'login' || modo === 'registro' || modo === 'esqueci') && (
              <>
                <label>E-mail</label>
                <input type="email" placeholder="Digite seu e-mail" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} required />
              </>
            )}
            
            {(modo === 'login' || modo === 'registro' || modo === 'reset') && (
              <>
                <label>{modo === 'reset' ? 'Nova Senha' : 'Senha'}</label>
                
                {/* CONTAINER ESTILIZADO PARA EMBUTIR O ÍCONE */}
                <div className="senha-wrapper">
                  <input 
                    type={mostrarSenha ? "text" : "password"} 
                    value={formData.senha} 
                    onChange={(e) => setFormData({...formData, senha: e.target.value})} 
                    required 
                    minLength="6" 
                    placeholder="Digite sua senha"
                  />
                  {/* BOTÃO DO ÍCONE (Posicionado de forma absoluta dentro do input) */}
                  <button 
                    type="button" 
                    className="btn-olho" 
                    onClick={() => setMostrarSenha(!mostrarSenha)} 
                    title={mostrarSenha ? "Ocultar senha" : "Exibir senha"}
                    tabIndex="-1" // Impede que o TAB foque no ícone antes do botão de enviar
                  >
                    {/* Renderiza o ÍCONE SVG correspondente ao estado */}
                    {mostrarSenha ? <IconeOlhoFechado /> : <IconeOlhoAberto />}
                  </button>
                </div>
              </>
            )}

            {modo === 'login' && (
               <div style={{ textAlign: 'right', marginTop: '-10px' }}>
                 <span style={{ fontSize: '0.8em', color: '#3498db', cursor: 'pointer' }} onClick={() => { 
                   setModo('esqueci'); 
                   setMensagem({tipo:'', texto:''}); 
                   setFormData({ nome: '', email: '', senha: '' }); /* Limpa o formulário */
                 }}>
                   Esqueci minha senha
                 </span>
               </div>
            )}

            <button type="submit" className="btn-login-submit" disabled={carregando}>
              {carregando ? 'Aguarde...' : 
               modo === 'registro' ? 'Criar Conta' : 
               modo === 'esqueci' ? 'Enviar Link de Recuperação' : 
               modo === 'reset' ? 'Salvar Nova Senha' : 'Entrar no Sistema'}
              
            </button>
          </form>

          {(modo === 'login' || modo === 'registro') && (
            <>
              <div style={{ margin: '20px 0', borderTop: '1px solid #eee', position: 'relative' }}>
                 <span style={{ position: 'absolute', top: '-10px', left: '50%', transform: 'translateX(-50%)', background: 'white', padding: '0 10px', fontSize: '0.85em', color: '#999' }}>ou</span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={() => setMensagem({ tipo: 'erro', texto: 'Erro ao conectar com o Google.' })}
                  text={modo === 'registro' ? "signup_with" : "signin_with"}
                  shape="rectangular"
                  size="large"
                  width="100%"
                />
              </div>
            </>
          )}

          <div className="login-toggle">
            {modo === 'login' ? 'Ainda não tem conta? ' : 
             modo === 'registro' ? 'Já tem uma conta? ' : ''}
            <span onClick={() => { 
              setModo(modo === 'login' ? 'registro' : 'login'); 
              setMensagem({tipo:'', texto:''}); 
              setFormData({ nome: '', email: '', senha: '' }); /* Limpa o formulário */
            }}>
              {modo === 'login' ? 'Cadastre-se' : 
               modo === 'registro' ? 'Faça Login' : 
               modo === 'esqueci' ? '← Voltar para o Login' : ''}
            </span>
          </div>
        </div>
      </div>
    </GoogleOAuthProvider>
  );
};

export default Login;