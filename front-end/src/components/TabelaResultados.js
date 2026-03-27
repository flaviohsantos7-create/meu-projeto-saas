import React from 'react';
import * as XLSX from 'xlsx';

const TabelaResultados = ({ artigos, aoVoltar }) => {
  const listaArtigos = Array.isArray(artigos) ? artigos : [];
  const artigosOrdenados = [...listaArtigos].sort((a, b) => (b.nota || 0) - (a.nota || 0));

  const truncarResumo = (texto) => {
      if (!texto || typeof texto !== 'string') return "Resumo indisponível.";
      const palavras = texto.trim().split(/\s+/); 
      if (palavras.length > 50) {
        return palavras.slice(0, 50).join(' ') + '...';
      }
      return texto;
    };

  const exportarExcel = () => {
    const ws = XLSX.utils.json_to_sheet(artigosOrdenados);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Resultados");
    XLSX.writeFile(wb, "Pesquisa_Academica.xlsx");
  };

  return (
    <div style={{ 
      width: 'max-content', 
      maxWidth: '95vw', /* MANTÉM NA TELA: O frame não ultrapassa o tamanho do monitor/celular */
      overflowX: 'auto', /* ROLAGEM INTELIGENTE: Cria rolagem interna se a tabela for muito grande */
      boxSizing: 'border-box', /* Garante que o padding não quebre o tamanho */
      position: 'relative', 
      left: '50%', 
      transform: 'translateX(-50%)',
      background: 'white',
      padding: '30px',
      borderRadius: '8px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      marginBottom: '40px'
    }}>
      
      <div className="header-tabela" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0 }}>Tabela Resumida de Artigos Científicos</h3>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn-voltar" style={{ margin: 0 }} onClick={aoVoltar}>Nova Pesquisa</button>
          <button className="btn-excel" style={{ margin: 0 }} onClick={exportarExcel}>📊 Exportar Excel</button>
        </div>
      </div>

      <table border="1" className="tabela-estilizada" style={{ borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'center', padding: '15px', whiteSpace: 'nowrap' }}>Nota</th>
            <th style={{ textAlign: 'center', padding: '15px', whiteSpace: 'nowrap' }}>Título do Artigo</th>
            <th style={{ textAlign: 'center', padding: '15px', whiteSpace: 'nowrap' }}>Principais Autores</th>
            <th style={{ textAlign: 'center', padding: '15px', whiteSpace: 'nowrap' }}>Resumo do Artigo</th>
            <th style={{ textAlign: 'center', padding: '15px', whiteSpace: 'nowrap' }}>Fonte</th>
            <th style={{ textAlign: 'center', padding: '15px', whiteSpace: 'nowrap' }}>Ano de Publicação</th>
            <th style={{ textAlign: 'center', padding: '15px', whiteSpace: 'nowrap' }}>Análise da IA (Justificativa)</th>
            <th style={{ textAlign: 'center', padding: '15px', whiteSpace: 'nowrap' }}>Link</th>
          </tr>
        </thead>
        <tbody>
          {artigosOrdenados.length > 0 ? (
            artigosOrdenados.map((art, index) => (
              <tr key={index}>
                <td className={art.nota > 70 ? "nota-alta" : art.nota >= 50 ? "nota-media" : "nota-baixa"} style={{ textAlign: 'center', padding: '15px' }}>
                  {art.nota}%
                </td>

                <td style={{ fontSize: '0.85em', padding: '15px', maxWidth: '250px' }}>
                  {art.titulo}
                </td>

                <td style={{ fontSize: '0.85em', padding: '15px', maxWidth: '250px' }}>
                  {art.autores}
                </td>

                <td style={{ fontSize: '0.85em', padding: '15px', maxWidth: '400px' }}>
                  {truncarResumo(art.resumo)}
                </td>

                <td style={{ textAlign: 'center', padding: '15px', whiteSpace: 'nowrap' }}>
                  <span className={`badge-fonte ${art.fonte ? art.fonte.toLowerCase().replace(/[\s/]+/g, '-') : ''}`}>
                    {art.fonte}
                  </span>
                </td>

                <td style={{ fontSize: '0.85em', padding: '15px', textAlign: 'center', whiteSpace: 'nowrap' }}>
                  {art.data}
                </td>

                <td className="coluna-resumo" style={{ fontSize: '0.85em', padding: '15px', verticalAlign: 'top', maxWidth: '250px' }}>
                  {art.justificativa}
                </td>
                
                <td style={{ fontSize: '0.95em', padding: '15px', textAlign: 'center', whiteSpace: 'nowrap' }}>
                  {art.url ? (
                    <a href={art.url} target="_blank" rel="noopener noreferrer" className="btn-link">
                      🔗 Acessar Artigo
                    </a>
                  ) : "-"}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="8" style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
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