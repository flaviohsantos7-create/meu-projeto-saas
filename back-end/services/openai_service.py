import json

# def gerar_chaves_e_contexto(dados_questionario, client):

#     respostas_usuario = f"""
#     Tema: {dados_questionario.get('tema')}
#     Problema: {dados_questionario.get('problema')}
#     Termos Obrigatórios: {dados_questionario.get('termos')}
#     Contexto/Aplicação: {dados_questionario.get('contexto')}
#     """

#     prompt_sistema = """
#     Você é um especialista em bibliometria. Com base nas respostas, gere um JSON com:
#     1. 'string_busca': Uma String Booleana otimizada (ex: "Termo A" AND "Termo B").
#     2. 'contexto_semantico': Um parágrafo técnico para filtragem de resumos.
#     """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": prompt_sistema},
#             {"role": "user", "content": respostas_usuario}
#         ],
#         response_format={ "type": "json_object" }
#     )
    
#     return json.loads(response.choices[0].message.content)
#_________________________________________________________________________________________________________________________________________________
def filtrar_artigos_com_ia(contexto_gerado, lista_artigos, client):
    artigos_ranqueados = []
    
    for artigo in lista_artigos:
        prompt = f"""
        CONTEXTO DE PESQUISA: {contexto_gerado}
        ---
        TÍTULO: {artigo.get('titulo')}
        RESUMO: {artigo.get('resumo')}
        ---
        Avalie a compatibilidade deste artigo com o contexto (0 a 100).
        Retorne APENAS um JSON: {{"nota": int, "justificativa": "string curta"}}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            
            analise = json.loads(response.choices[0].message.content)
            
            artigo_completo = {**artigo, **analise}
            artigos_ranqueados.append(artigo_completo)
            
        except Exception as e:
            print(f"Erro ao analisar o artigo {artigo.get('titulo')}: {e}")

    return sorted(artigos_ranqueados, key=lambda x: x.get('nota', 0), reverse=True)
#_________________________________________________________________________________________________________________________________________________
def gerar_chaves_e_contexto(dados_questionario, client):
    # Teste sem IA
        return {
            "string_busca": '("Industry 4.0" OR "Automation") AND "Waste"',
            "contexto_semantico": "Artigos focados em automação industrial e redução de resíduos."
        }