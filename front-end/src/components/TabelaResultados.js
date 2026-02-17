import React from 'react';

const TabelaResultados = ({ artigos, aoVoltar }) => {
  return (
    <div className="container-tabela">
      <div className="header-tabela">
        <h3>Tabela Resumida de Artigos Científicos</h3>
        <button className="btn-voltar" onClick={aoVoltar}>Nova Pesquisa</button>
      </div>
      
      <p>Artigos encontrados com alto índice de compatibilidade:</p>

      <table border="1" style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#f2f2f2' }}>
            <th>Nota</th>
            <th>Título do Artigo</th>
            <th>Autores</th>
            <th>Data</th>
            <th>Resumo e Justificativa IA</th>
          </tr>
        </thead>
        <tbody>
          {artigos.map((art, index) => (
            <tr key={index}>
              <td style={{ fontWeight: 'bold', color: art.nota > 70 ? 'green' : 'orange' }}>
                {art.nota}%
              </td>
              <td>{art.titulo}</td>
              <td>{art.autores}</td>
              <td>{art.data}</td>
              <td>
                <strong>Resumo:</strong> {art.resumo.substring(0, 200)}...
                <br />
                <br />
                <strong>Por que ler este artigo?</strong> 
                <p style={{ fontStyle: 'italic', color: '#555' }}>"{art.justificativa}"</p>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TabelaResultados;