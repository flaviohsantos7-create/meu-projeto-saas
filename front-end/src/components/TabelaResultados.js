import React from 'react';
import * as XLSX from 'xlsx';

const TabelaResultados = ({ artigos, aoVoltar }) => {
  const listaArtigos = Array.isArray(artigos) ? artigos : [];

  const exportarExcel = () => {
  const ws = XLSX.utils.json_to_sheet(artigos);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Resultados");
  XLSX.writeFile(wb, "Pesquisa_Academica.xlsx");
  };

  return (
    <div className="container-tabela">
      <div className="header-tabela">
        <h3>Tabela Resumida de Artigos Científicos</h3>
        <button className="btn-voltar" onClick={aoVoltar}>Nova Pesquisa</button>
      </div>

      <button onClick={exportarExcel} className="btn-excel">📊 Exportar Excel</button>

      <table border="1" className="tabela-estilizada">
      <thead>
        <tr>
          <th style={{ width: '80px' }}>Nota</th>
          <th style={{ width: '250px' }}>Título do Artigo</th>
          <th>Resumo do Artigo</th>
          <th style={{ width: '250px' }}>Fonte</th>
          <th style={{ width: '250px' }}>Ano de Publicação</th>
          <th>Análise da IA (Justificativa)</th>
          <th style={{ width: '100px' }}>Link</th>
        </tr>
      </thead>
        <tbody>
          {listaArtigos.length > 0 ? (
            listaArtigos.map((art, index) => (
              <tr key={index}>
                {/* Coluna de Nota com as cores que você já ajustou */}
                <td className={art.nota > 70 ? "nota-alta" : art.nota >= 50 ? "nota-media" : "nota-baixa"}>
                  {art.nota}%
                </td>
                <td>{art.titulo}</td>
                <td>{art.titulo}</td>
                {/* Nova Coluna de Fonte */}
                <td>
                  <span className={`badge-fonte ${art.fonte?.toLowerCase().replace(/\s/g, '-')}`}>
                    {art.fonte}
                  </span>
                </td>

                <td>{art.data}</td>

                <td className="coluna-resumo">
                  <strong>Justificativa:</strong> {art.justificativa}
                  <br /><br />
                </td>
                
                <td>
                {art.url && (
                  <a href={art.url} target="_blank" rel="noopener noreferrer" className="btn-link">
                    🔗 Acessar Artigo
                  </a>
                )}
                </td>
                
              </tr>
            ))
          ) : (
        
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