import React from 'react';

const TabelaResultados = ({ artigos, aoVoltar }) => {
  // Garante que 'artigos' seja sempre uma lista para evitar erros de renderização
  const listaArtigos = Array.isArray(artigos) ? artigos : [];

  return (
    <div className="container-tabela">
      <div className="header-tabela">
        <h3>Tabela Resumida de Artigos Científicos</h3>
        <button className="btn-voltar" onClick={aoVoltar}>Nova Pesquisa</button>
      </div>

      <table border="1" className="tabela-estilizada">
        <thead>
          <tr>
            <th>Nota</th>
            <th>Título do Artigo</th>
            <th>Autores</th>
            <th>Data</th>
            <th>Resumo e Justificativa IA</th>
          </tr>
        </thead>
        <tbody>
          {listaArtigos.length > 0 ? (
            // Se houver artigos, renderiza as linhas normalmente
            listaArtigos.map((art, index) => (
              <tr key={index}>
                <td className="nota-high">{art.nota}%</td>
                <td>{art.titulo}</td>
                <td>{art.autores}</td>
                <td>{art.data}</td>
                <td className="coluna-resumo">
                  <strong>Resumo:</strong> {art.resumo?.substring(0, 150)}...
                  <br /><br />
                  <strong>Justificativa:</strong> {art.justificativa}
                </td>
              </tr>
            ))
          ) : (
            // Se a lista estiver vazia, renderiza uma linha única ocupando todas as colunas
            <tr>
              <td colSpan="5" style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                <div className="feedback-vazio">
                  <strong>Nenhum artigo encontrado.</strong>
                  <p>Tente ajustar os termos da sua busca ou o contexto semântico.</p>
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default TabelaResultados;