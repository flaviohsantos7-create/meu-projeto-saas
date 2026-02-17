const API_URL = "http://localhost:5000";

export const gerarContexto = async (dados) => {
    const response = await fetch(`${API_URL}/gerar-contexto`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    });
    return response.json();
};

export const buscarArtigos = async (dadosBusca) => {
    const response = await fetch(`${API_URL}/buscar-artigos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dadosBusca)
    });
    return response.json();
};