
import mysql.connector
import os
from dotenv import load_dotenv
import google.generativeai as genai # Importar a biblioteca do Gemini

load_dotenv()

# Função para chamar a API do Gemini e gerar a query SQL
def gerar_query_sql(pergunta: str, colunas: dict) -> str:
    # Configurar a chave da API do Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        return "Erro: Chave da API do Gemini não encontrada no .env"
    
    genai.configure(api_key=gemini_api_key)
    
    # Criação do prompt para o Gemini, incluindo as colunas do banco
    # O prompt pode ser similar, mas a instrução do "system role" é embutida no prompt do usuário
    prompt = f"""
Você é um assistente de SQL que opera para o banco de dados fictício chamado "querypilot".
Seu objetivo é gerar APENAS a query SQL solicitada, sem nenhuma explicação adicional, introdução ou formatação markdown como ```sql.
A query deve ser compatível com MySQL e referente ao banco de dados "querypilot".

Estrutura do banco de dados:
{colunas}

Pergunta do usuário: {pergunta}
Query SQL:
"""
    
    try:
        # Configurações de geração (opcional, mas útil para controlar a saída)
        generation_config = {
            "temperature": 0.1, # Mais baixo para respostas mais determinísticas/factuais
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048, # Aumentar se as queries forem longas
        }

        # Escolha o modelo Gemini (gemini-pro é um bom modelo de texto)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest", # ou "gemini-pro" ou "gemini-1.5-flash-latest"
            generation_config=generation_config
        )
        
        response = model.generate_content(prompt)
        
        # Obtendo a resposta gerada
        query = response.text.strip()
        
        # Remover qualquer marcação de código (```sql ou ``` no final) - pode não ser necessário se o prompt for bem instruído
        query = query.replace("```sql", "").replace("```", "").strip()
        
        return query
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        # Tentar extrair mais detalhes se for um erro específico da API do Google
        if hasattr(e, 'message'):
            print(f"Detalhe do erro da API: {e.message}")
        return f"Erro ao gerar query com Gemini: {e}"


# Função para obter as tabelas e colunas do banco de dados (permanece a mesma)
def obter_estruturas_tabelas() -> dict:
    try:
        # Certifique-se que o nome do banco no .env é 'querypilot' ou o que você estiver usando
        db_name = os.getenv("MYSQL_DB", "querypilot") # Adicionado valor padrão
        
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=db_name, # Usar a variável
            # As opções abaixo podem não ser necessárias para o Gemini, mas são para o MySQL
            # auth_plugin='mysql_native_password' # Remova ou comente se causar problemas
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tabelas_raw = cursor.fetchall()

        # Verificar se tabelas_raw não está vazio
        if not tabelas_raw:
            cursor.close()
            conn.close()
            print(f"Nenhuma tabela encontrada no banco de dados '{db_name}'.")
            return {} # Retorna dicionário vazio se não houver tabelas

        tabelas = [t[0] for t in tabelas_raw] # Extrai o nome da tabela

        colunas_dict = {}
        for tabela_nome in tabelas:
            cursor.execute(f"DESCRIBE `{tabela_nome}`;") # Use backticks para nomes de tabela
            colunas_tabela_raw = cursor.fetchall()
            colunas_dict[tabela_nome] = [col[0] for col in colunas_tabela_raw]
        
        cursor.close()
        conn.close()
        return colunas_dict
    except Exception as e:
        print(f"Erro ao obter estrutura das tabelas: {e}")
        return {} # Retornar dicionário vazio em caso de erro

# Função simples que executa a query SQL (permanece a mesma)
def executar_query_func(query: str): # Removido anotação de tipo de retorno para simplificar
    """Executa uma query SQL real no banco MySQL e retorna os resultados."""
    if query.startswith("Erro ao gerar query"): # Não tentar executar se a geração falhou
        print(f"Não foi possível executar a query devido a erro anterior: {query}")
        return None

    try:
        # Certifique-se que o nome do banco no .env é 'querypilot' ou o que você estiver usando
        db_name = os.getenv("MYSQL_DB", "querypilot") # Adicionado valor padrão

        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""), # Senha padrão vazia se não definida
            database=db_name, # Usar a variável
            # auth_plugin='mysql_native_password' # Remova ou comente se causar problemas
        )
        cursor = conn.cursor()
        print(f"Executando query: {query}") # Debug: mostrar a query
        cursor.execute(query)
        
        # Para SELECT, fetchall. Para INSERT/UPDATE/DELETE, verificar rowcount e commitar.
        if query.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
        else:
            conn.commit() # Importante para INSERT, UPDATE, DELETE
            results = f"Comando executado com sucesso. Linhas afetadas: {cursor.rowcount}"
        
        cursor.close()
        conn.close()

        return results
    except mysql.connector.Error as err: # Captura erros específicos do MySQL
        print(f"Erro ao executar query no MySQL: {err}")
        print(f"Query com erro: {query}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao executar query: {e}")
        print(f"Query com erro: {query}")
        return None

# Exemplo de interação com o agente
print("Obtendo estrutura das tabelas...")
estrutura_db = obter_estruturas_tabelas()

if not estrutura_db: # Se não conseguiu obter a estrutura, não prosseguir
    print("Não foi possível obter a estrutura do banco. Saindo.")
else:
    print("Estrutura do banco obtida com sucesso.")
    print(f"Estrutura: {estrutura_db}") # Debug: mostrar a estrutura

    pergunta = input("Realize a sua pergunta ao nosso agente: ")

    print("Gerando query SQL com Gemini...")
    query_gerada = gerar_query_sql(pergunta, estrutura_db)

    print(f"\nQUERY GERADA: `{query_gerada}`")
    
    if query_gerada and not query_gerada.startswith("Erro"):
        print(f"\nRESULTADO:")
        resultado_execucao = executar_query_func(query_gerada)
        if resultado_execucao is not None:
            print(resultado_execucao)
        else:
            print("Falha ao executar a query ou query não retornou resultados.")
    else:
        print("Não foi possível gerar uma query SQL válida.")