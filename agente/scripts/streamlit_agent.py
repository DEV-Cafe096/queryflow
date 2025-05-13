
# import streamlit as st
# import mysql.connector
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv
# import json

# load_dotenv()



# # --- FUNÇÃO PARA LISTAR MODELOS DISPONÍVEIS (PARA DEBUG) ---
# def listar_modelos_disponiveis_no_streamlit(chave_api):
#     if not chave_api:
#         st.sidebar.error("Chave da API Gemini não fornecida para listar modelos.")
#         return

#     try:
#         genai.configure(api_key=chave_api)
        
#         model_list_str = "Modelos Gemini disponíveis que suportam 'generateContent':\n"
#         found_models = False
#         for m in genai.list_models():
#           if 'generateContent' in m.supported_generation_methods:
#             model_list_str += f"- {m.name}\n" # Usar m.name que é o identificador correto
#             found_models = True
        
#         if found_models:
#             st.sidebar.info(model_list_str)
#         else:
#             st.sidebar.warning("Nenhum modelo encontrado que suporte 'generateContent'.")
            
#     except Exception as e:
#         st.sidebar.error(f"Erro ao listar modelos Gemini: {e}")

# # --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
# st.set_page_config(page_title="QueryFlow Consultas", page_icon="📑", layout="wide")
# st.title("☕ QueryFlow Consultas")

# # Carregar CSS
# with open("style.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# # --- CONFIGURAÇÃO DA SIDEBAR (INSERÇÃO DE CREDENCIAIS) ---
# st.sidebar.header("🔐 Configurações")
# gemini_api_key = st.sidebar.text_input(
#     "Chave da API Gemini", 
#     type="password", 
#     key="gemini_key_input", 
#     value=os.getenv("GEMINI_API_KEY", "") # Carregar do .env se existir
# )
# mysql_host = st.sidebar.text_input(
#     "MySQL Host", 
#     value=os.getenv("MYSQL_HOST", "localhost"), 
#     key="mysql_host_input"
# )
# mysql_user = st.sidebar.text_input(
#     "Usuário MySQL", 
#     value=os.getenv("MYSQL_USER", "root"), 
#     key="mysql_user_input"
# )
# mysql_password = st.sidebar.text_input(
#     "Senha MySQL", 
#     type="password", 
#     value=os.getenv("MYSQL_PASSWORD", ""), 
#     key="mysql_password_input"
# )
# mysql_db = st.sidebar.text_input(
#     "Nome do Banco de Dados", 
#     value=os.getenv("MYSQL_DB", "querypilot"), 
#     key="mysql_db_input"
# )

# # Botão para listar modelos na sidebar
# if st.sidebar.button("Listar Modelos Gemini Disponíveis", key="btn_list_models"):
#     listar_modelos_disponiveis_no_streamlit(gemini_api_key)

# # --- MEIO: INTERAÇÃO COM O USUÁRIO E ENTRADA DA PERGUNTA ---
# if "pergunta" not in st.session_state:
#     st.session_state.pergunta = ""
# if "query_sql" not in st.session_state:
#     st.session_state.query_sql = ""
# if "resultados_db" not in st.session_state:
#     st.session_state.resultados_db = []
# if "colunas_resultado" not in st.session_state:
#     st.session_state.colunas_resultado = []


# st.markdown("### 💬 Sugestões de perguntas")
# sugestoes_col1, sugestoes_col2 = st.columns(2)
# with sugestoes_col1:
#     if st.button("📋 Listar todos os clientes", key="btn_clientes",):
#         st.session_state.pergunta = "Me mostre todos os clientes"
#     if st.button("🏠 Listar todos os endereços", key="btn_enderecos",):
#         st.session_state.pergunta = "Me mostre todos os endereços"
# with sugestoes_col2:
#     if st.button("💸 Listar todos os pagamentos", key="btn_pagamentos",):
#         st.session_state.pergunta = "Me mostre todos os pagamentos"
#     if st.button("📈 Listar todas as movimentações", key="btn_movimentacoes",):
#         st.session_state.pergunta = "Me mostre todas as movimentações"


# st.markdown("### ❓ Pergunta personalizada")
# pergunta_usuario_input = st.text_input(
#     "Digite sua pergunta em linguagem natural:",
#     value=st.session_state.pergunta,
#     key=f"input_pergunta_{st.session_state.pergunta}" # Forçar recriação se sugestão mudar
# )


# # --- FUNÇÕES AUXILIARES ---
# @st.cache_data(ttl=3600) # Cache da estrutura do DB por 1 hora
# def obter_estruturas_tabelas_cached(_mysql_host, _mysql_user, _mysql_password, _mysql_db):
#     # Wrapper para permitir cache, já que os inputs da sidebar não são hashable diretamente
#     if not all([_mysql_host, _mysql_user, _mysql_db]):
#         return {} # Não tentar conectar se faltar dados essenciais
#     try:
#         conn = mysql.connector.connect(
#             host=_mysql_host, user=_mysql_user, password=_mysql_password, database=_mysql_db,
#             connect_timeout=5, 
#         )
#         cursor = conn.cursor()
#         cursor.execute("SHOW TABLES;")
#         tabelas_raw = cursor.fetchall()

#         if not tabelas_raw:
#             st.toast(f"Nenhuma tabela encontrada no banco '{_mysql_db}'.", icon="⚠️")
#             cursor.close()
#             conn.close()
#             return {}

#         tabelas = [t[0] for t in tabelas_raw]
#         colunas_dict = {}
#         for tabela_nome in tabelas:
#             cursor.execute(f"DESCRIBE `{tabela_nome}`;")
#             colunas_tabela_raw = cursor.fetchall()
#             colunas_dict[tabela_nome] = [col[0] for col in colunas_tabela_raw]
#         cursor.close()
#         conn.close()
#         return colunas_dict
#     except mysql.connector.Error as err:
#         st.error(f"Erro no MySQL ao obter estrutura: {err}")
#         return {}
#     except Exception as e:
#         st.error(f"Erro inesperado ao obter estrutura: {e}")
#         return {}

# @st.cache_data # Cache do prompt.json
# def carregar_prompt_contexto_cached():
#     try:
#         with open("protocolos/prompt.json", "r", encoding="utf-8") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         st.toast("Arquivo 'protocolos/prompt.json' não encontrado. Usando prompt genérico.", icon="⚠️")
#         return {
#             "model_role": "Você é um assistente de SQL que opera para o banco de dados fictício chamado \"queryflow\". Seu objetivo é gerar APENAS a query SQL solicitada, sem nenhuma explicação adicional, introdução ou formatação markdown como ```sql. A query deve ser compatível com MySQL.",
#             "restricoes": [], "instrucoes_sql": []
#         }
#     except Exception as e:
#         st.error(f"Erro ao carregar o contexto do prompt: {e}")
#         return {}

# def gerar_query_sql_com_gemini(pergunta_user: str, colunas_db: dict, chave_api: str, modelo_gemini: str):
#     if not chave_api:
#         st.error("Chave da API Gemini não fornecida.")
#         return ""
#     if not modelo_gemini:
#         st.error("Nome do modelo Gemini não especificado.")
#         return ""
    
#     try:
#         genai.configure(api_key=chave_api)
#     except Exception as e:
#         st.error(f"Erro ao configurar a API do Gemini: {e}")
#         return ""

#     contexto_prompt_base = carregar_prompt_contexto_cached()
    
#     prompt_completo = f"""{contexto_prompt_base.get('model_role', "Você é um assistente de SQL.")}
# Você opera para o banco de dados chamado '{mysql_db}'.
# Seu objetivo é gerar APENAS a query SQL solicitada, sem nenhuma explicação adicional, introdução ou formatação markdown como ```sql.
# A query deve ser compatível com MySQL.

# Restrições: {'; '.join(contexto_prompt_base.get('restricoes', []))}
# Instruções SQL adicionais: {'; '.join(contexto_prompt_base.get('instrucoes_sql', []))}

# Estrutura do banco de dados (tabelas e colunas):
# {json.dumps(colunas_db, indent=2, ensure_ascii=False)}

# Pergunta do usuário: {pergunta_user}

# Query SQL:
# """
#     try:
#         generation_config = {"temperature": 0.1, "max_output_tokens": 2048}
#         model = genai.GenerativeModel(
#             model_name=modelo_gemini, # Usar o modelo especificado
#             generation_config=generation_config
#         )
#         response = model.generate_content(prompt_completo)
#         query = response.text.strip().replace("```sql", "").replace("```", "").strip()
#         return query
#     except Exception as e:
#         st.error(f"Erro ao chamar API Gemini (Modelo: {modelo_gemini}): {e}")
#         return ""

# def executar_query_mysql(query_sql: str):
#     if not query_sql: return [], []
#     if not all([mysql_host, mysql_user, mysql_db]): return [], []
#     try:
#         conn = mysql.connector.connect(
#             host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_db,
#             connect_timeout=5, 
#         )
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute(query_sql)
        
#         cols = []
#         res = []
#         if query_sql.strip().upper().startswith("SELECT"):
#             res = cursor.fetchall()
#             if res: cols = list(res[0].keys())
#         else:
#             conn.commit()
#             st.toast(f"Comando DML executado. Linhas afetadas: {cursor.rowcount}", icon="✔️")
#         cursor.close()
#         conn.close()
#         return cols, res
#     except mysql.connector.Error as err:
#         st.error(f"Erro no MySQL ao executar query: {err}")
#         st.code(f"Query com erro:\n{query_sql}", language="sql")
#         return [], []
#     except Exception as e:
#         st.error(f"Erro inesperado ao executar query: {e}")
#         st.code(f"Query com erro:\n{query_sql}", language="sql")
#         return [], []

# def salvar_historico_db(pergunta, query, resultado):
#     # Implementação simplificada, idealmente seria assíncrono ou em thread separada
#     if not all([mysql_host, mysql_user, mysql_db]): return
#     try:
#         conn = mysql.connector.connect(
#             host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_db,
#             # allow_public_key_retrieval=True
#         )
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS historico_interacoes (
#                 id INT AUTO_INCREMENT PRIMARY KEY, pergunta TEXT, query_gerada TEXT,
#                 resultado LONGTEXT, feedback VARCHAR(10), data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             );""")
#         cursor.execute(
#             "INSERT INTO historico_interacoes (pergunta, query_gerada, resultado) VALUES (%s, %s, %s)",
#             (pergunta, query, json.dumps(resultado, ensure_ascii=False, default=str))
#         )
#         conn.commit()
#         cursor.close()
#         conn.close()
#     except Exception as e:
#         st.warning(f"Erro ao salvar histórico: {e}") # Warning para não interromper fluxo principal

# def salvar_feedback_db(pergunta, feedback):
#     # Implementação simplificada
#     if not all([mysql_host, mysql_user, mysql_db]): return
#     try:
#         conn = mysql.connector.connect(
#             host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_db,
#             # allow_public_key_retrieval=True
#         )
#         cursor = conn.cursor()
#         # Garante que a tabela existe (para o caso de ser a primeira execução)
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS historico_interacoes (
#                 id INT AUTO_INCREMENT PRIMARY KEY, pergunta TEXT, query_gerada TEXT,
#                 resultado LONGTEXT, feedback VARCHAR(10), data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             );""")
#         cursor.execute("""
#             UPDATE historico_interacoes SET feedback = %s 
#             WHERE id = (SELECT id FROM (
#                             SELECT id FROM historico_interacoes WHERE pergunta = %s ORDER BY data DESC LIMIT 1
#                         ) AS subquery)
#         """, (feedback, pergunta))
#         conn.commit()
#         if cursor.rowcount == 0: st.toast("Histórico não encontrado para salvar feedback.", icon="⚠️")
#         cursor.close()
#         conn.close()
#     except Exception as e:
#         st.warning(f"Erro ao salvar feedback: {e}")


# # --- LÓGICA PRINCIPAL DA APLICAÇÃO ---

# # Input para o usuário escolher o modelo Gemini (após listá-los)
# MODELO_GEMINI_ESCOLHIDO = st.sidebar.text_input(
#     "Nome do Modelo Gemini a ser usado (da lista acima):", 
#     value=os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-latest"), # Default para um modelo comum e rápido
#     key="gemini_model_name_input"
# )


# if st.button("Gerar e Executar Consulta SQL", key="btn_executar", type="primary", use_container_width=True):
#     if pergunta_usuario_input:
#         st.session_state.pergunta = pergunta_usuario_input # Atualiza o estado com a pergunta atual
        
#         if not gemini_api_key:
#             st.error("Chave da API Gemini não fornecida na sidebar.")
#         elif not MODELO_GEMINI_ESCOLHIDO:
#             st.error("Nome do Modelo Gemini não especificado na sidebar.")
#         elif not all([mysql_host, mysql_user, mysql_db]):
#             st.error("Configurações do MySQL incompletas na sidebar.")
#         else:
#             with st.spinner("Obtendo estrutura do banco de dados..."):
#                 estrutura_db = obter_estruturas_tabelas_cached(mysql_host, mysql_user, mysql_password, mysql_db)
            
#             if estrutura_db:
#                 st.toast("Estrutura do banco de dados obtida.", icon="📄")
#                 with st.spinner(f"Gerando SQL com {MODELO_GEMINI_ESCOLHIDO}..."):
#                     st.session_state.query_sql = gerar_query_sql_com_gemini(
#                         st.session_state.pergunta, estrutura_db, gemini_api_key, MODELO_GEMINI_ESCOLHIDO
#                     )

#                 if st.session_state.query_sql and not st.session_state.query_sql.startswith("Erro"):
#                     with st.spinner("Executando consulta SQL no banco de dados..."):
#                         st.session_state.colunas_resultado, st.session_state.resultados_db = executar_query_mysql(
#                             st.session_state.query_sql
#                         )
                    
#                     if st.session_state.resultados_db or not st.session_state.query_sql.strip().upper().startswith("SELECT"):
#                         salvar_historico_db(st.session_state.pergunta, st.session_state.query_sql, st.session_state.resultados_db)
                    
#                 else: # Falha ao gerar SQL
#                     st.session_state.resultados_db = []
#                     st.session_state.colunas_resultado = []
#             else: # Falha ao obter estrutura
#                 st.error("Não foi possível obter a estrutura do banco. Verifique as configurações e logs.")
#                 st.session_state.query_sql = ""
#                 st.session_state.resultados_db = []
#                 st.session_state.colunas_resultado = []
#     else:
#         st.warning("Por favor, digite uma pergunta.")

# # Exibição dos resultados e feedback fora do bloco do botão "Gerar" para persistir na tela
# if st.session_state.query_sql and not st.session_state.query_sql.startswith("Erro"):
#     st.markdown("---")
#     st.markdown("####  resultados da consulta SQL")
#     st.markdown("---")
    
#     mostrar_sql = st.toggle("👁️ Mostrar consulta SQL", value=True, key="toggle_sql_display")
#     if mostrar_sql:
#         st.code(st.session_state.query_sql, language="sql")

#     if st.session_state.resultados_db:
#         st.success(f"✅ Consulta realizada! {len(st.session_state.resultados_db)} linha(s) retornada(s).")
#         st.dataframe(st.session_state.resultados_db, use_container_width=True)
#     elif st.session_state.query_sql.strip().upper().startswith("SELECT"):
#         st.info("ℹ️ A consulta SQL foi executada, mas não retornou resultados.")
#     # Mensagem para DML já é dada por toast

#     # Feedback
#     st.markdown("---")
#     feedback_key = f"feedback_radio_{hash(st.session_state.pergunta)}_{hash(st.session_state.query_sql)}"
#     feedback_selecionado = st.radio(
#         "Essa resposta foi útil?",
#         ("👍 Sim", "👎 Não"),
#         index=None,
#         key=feedback_key,
#         horizontal=True
#     )
#     if feedback_selecionado:
#         salvar_feedback_db(st.session_state.pergunta, feedback_selecionado)
#         st.toast(f"Feedback '{feedback_selecionado}' salvo!", icon="👍" if feedback_selecionado == "👍 Sim" else "👎")
# elif st.session_state.query_sql and st.session_state.query_sql.startswith("Erro"):
#     st.error(f"Falha na geração da query: {st.session_state.query_sql}")

import streamlit as st
import mysql.connector
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(
    page_title="QueryFlow", 
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNÇÃO PARA CARREGAR CSS EXTERNO ---
def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        print(f"AVISO: Arquivo CSS '{file_name}' não encontrado.")
    except Exception as e:
        print(f"AVISO: Erro ao carregar CSS '{file_name}': {e}")

# --- APLICAR CSS EXTERNO ---
local_css("style.css") 

# --- DEFINIÇÕES DAS FUNÇÕES AUXILIARES ---
# (COLE SUAS FUNÇÕES COMPLETAS AQUI: listar_modelos, obter_estruturas, carregar_prompt, etc.)
# ... (Suas funções auxiliares como definidas anteriormente) ...
def listar_modelos_disponiveis_no_streamlit(chave_api): # Sua função
    if not chave_api:
        st.sidebar.error("Chave da API Gemini não fornecida para listar modelos.")
        return
    try:
        genai.configure(api_key=chave_api)
        model_list_str = "Modelos Gemini disponíveis que suportam 'generateContent':\n"
        found_models = False
        for m in genai.list_models():
          if 'generateContent' in m.supported_generation_methods:
            model_list_str += f"- {m.name}\n"
            found_models = True
        if found_models:
            st.sidebar.info(model_list_str)
        else:
            st.sidebar.warning("Nenhum modelo encontrado que suporte 'generateContent'.")
    except Exception as e:
        st.sidebar.error(f"Erro ao listar modelos Gemini: {e}")

@st.cache_data(ttl=3600)
def obter_estruturas_tabelas_cached(_mysql_host, _mysql_user, _mysql_password, _mysql_db): # Sua função
    if not all([_mysql_host, _mysql_user, _mysql_db]): 
        print("Alerta: Configurações do MySQL incompletas para obter estrutura.")
        return {"error": "Configurações do MySQL incompletas."}
    try:
        conn = mysql.connector.connect(
            host=_mysql_host, user=_mysql_user, password=_mysql_password, database=_mysql_db,
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tabelas_raw = cursor.fetchall()
        if not tabelas_raw:
            print(f"Alerta: Nenhuma tabela encontrada no banco '{_mysql_db}'.")
            cursor.close(); conn.close(); return {} 
        tabelas = [t[0] for t in tabelas_raw]
        colunas_dict = {}
        for tabela_nome in tabelas:
            cursor.execute(f"DESCRIBE `{tabela_nome}`;")
            colunas_tabela_raw = cursor.fetchall()
            colunas_dict[tabela_nome] = [col[0] for col in colunas_tabela_raw]
        cursor.close(); conn.close()
        return colunas_dict
    except mysql.connector.Error as err: 
        print(f"Erro MySQL (estrutura): {err}")
        return {"error": f"Erro MySQL (estrutura): {str(err)}"}
    except Exception as e: 
        print(f"Erro inesperado (estrutura): {e}")
        return {"error": f"Erro inesperado (estrutura): {str(e)}"}

@st.cache_data
def carregar_prompt_contexto_cached(): # Sua função
    try:
        with open("../../protocolos/prompt.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Alerta: Arquivo '../../protocolos/prompt.json' não encontrado. Usando prompt genérico.")
        return {
            "model_role": "Você é um assistente SQL para o banco QueryFlow. Gere APENAS a query SQL (MySQL) sem explicações ou markdown.",
            "restricoes": ["Não use `SELECT *` a menos que explicitamente pedido."], "instrucoes_sql": []
        }
    except Exception as e: 
        print(f"Erro ao carregar prompt.json: {e}")
        return {"error": f"Erro ao carregar prompt.json: {str(e)}"}

def gerar_query_sql_com_gemini(pergunta_user: str, colunas_db: dict, chave_api: str, modelo_gemini: str, db_name_from_input: str): # Sua função
    if not chave_api: return "Erro: Chave API Gemini não fornecida."
    if not modelo_gemini: return "Erro: Modelo Gemini não especificado."
    if isinstance(colunas_db, dict) and colunas_db.get("error"): 
        return f"Erro: Não foi possível obter estrutura do banco - {colunas_db['error']}"
    if not colunas_db:
        return "Erro: Estrutura do banco de dados está vazia ou não pôde ser carregada."
    try:
        genai.configure(api_key=chave_api)
        contexto_prompt_base = carregar_prompt_contexto_cached()
        if isinstance(contexto_prompt_base, dict) and contexto_prompt_base.get("error"): 
            return f"Erro: Falha ao carregar contexto do prompt - {contexto_prompt_base['error']}"
        
        prompt_completo = f"""{contexto_prompt_base.get('model_role', 'Você é um assistente SQL.')}
Database: {db_name_from_input} 
Estrutura: {json.dumps(colunas_db, indent=2, ensure_ascii=False)}
Restrições: {'; '.join(contexto_prompt_base.get('restricoes', []))}
Instruções SQL: {'; '.join(contexto_prompt_base.get('instrucoes_sql', []))}
Pergunta: {pergunta_user}
Query SQL:"""
        generation_config = {"temperature": 0.05, "max_output_tokens": 2048}
        model = genai.GenerativeModel(model_name=modelo_gemini, generation_config=generation_config)
        response = model.generate_content(prompt_completo)
        query = response.text.strip().replace("```sql", "").replace("```", "").strip()
        if not query: return "Erro: Gemini retornou uma query vazia."
        return query
    except Exception as e:
        print(f"Erro API Gemini (Modelo: {modelo_gemini}): {e}")
        return f"Erro: API Gemini falhou - {str(e)}"

def executar_query_mysql(query_sql: str, _mysql_host, _mysql_user, _mysql_password, _mysql_db): # Sua função
    if not query_sql: return [], {"error": "Query SQL está vazia."}
    if not all([_mysql_host, _mysql_user, _mysql_db]): 
        return None, {"error": "Configurações do MySQL incompletas."} 
    try:
        conn = mysql.connector.connect(
            host=_mysql_host, user=_mysql_user, password=_mysql_password, database=_mysql_db,
            connect_timeout=5
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query_sql)
        res = []
        if query_sql.strip().upper().startswith("SELECT"):
            res = cursor.fetchall()
        else: 
            conn.commit()
            res = {"status": "Comando executado com sucesso", "linhas_afetadas": cursor.rowcount}
        cursor.close(); conn.close()
        return [], res 
    except mysql.connector.Error as err:
        print(f"Erro MySQL (execução): {err}")
        return [], {"error": f"Erro MySQL ao executar query: {str(err)}", "query_com_erro": query_sql}
    except Exception as e:
        print(f"Erro inesperado (execução): {e}")
        return [], {"error": f"Erro inesperado ao executar query: {str(e)}", "query_com_erro": query_sql}

def salvar_historico_db(pergunta, query, resultado, _mysql_host, _mysql_user, _mysql_password, _mysql_db): # Sua função
    if not all([_mysql_host, _mysql_user, _mysql_db]): return
    try:
        conn = mysql.connector.connect(host=_mysql_host, user=_mysql_user, password=_mysql_password, database=_mysql_db)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS historico_interacoes (id INT AUTO_INCREMENT PRIMARY KEY, pergunta TEXT, query_gerada TEXT, resultado LONGTEXT, feedback VARCHAR(10), data TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
        cursor.execute("INSERT INTO historico_interacoes (pergunta, query_gerada, resultado) VALUES (%s, %s, %s)", (pergunta, query, json.dumps(resultado, ensure_ascii=False, default=str)))
        conn.commit(); cursor.close(); conn.close()
    except Exception as e: 
        print(f"Aviso: Erro ao salvar histórico: {e}")

def salvar_feedback_db(pergunta, feedback, _mysql_host, _mysql_user, _mysql_password, _mysql_db): # Sua função
    if not all([_mysql_host, _mysql_user, _mysql_db]): return
    try:
        conn = mysql.connector.connect(host=_mysql_host, user=_mysql_user, password=_mysql_password, database=_mysql_db)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS historico_interacoes (id INT AUTO_INCREMENT PRIMARY KEY, pergunta TEXT, query_gerada TEXT, resultado LONGTEXT, feedback VARCHAR(10), data TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
        update_query = """
            UPDATE historico_interacoes SET feedback = %s 
            WHERE id = (
                SELECT id FROM (
                    SELECT id FROM historico_interacoes 
                    WHERE pergunta = %s 
                    ORDER BY data DESC LIMIT 1
                ) AS subquery
            )"""
        cursor.execute(update_query, (feedback, pergunta))
        conn.commit()
        if cursor.rowcount == 0: 
            print("Aviso: Histórico não encontrado para salvar feedback.")
        cursor.close(); conn.close()
    except Exception as e: 
        print(f"Aviso: Erro ao salvar feedback: {e}")

# --- TÍTULO E SUBTÍTULO ---
st.markdown("<div style='text-align: center; margin-bottom: 10px;'><span style='font-size: 2.5em; font-weight: bold;'>🌊 QueryFlow</span> <span style='font-size: 1.2em; color: #B0BEC5; margin-bottom:10px  vertical-align: middle;'>Consultas com Gemini AI</span></div>", unsafe_allow_html=True)
st.markdown("<p align='center' style='margin-bottom: 2.5rem; font-size: 1.1rem; color: #9E9E9E;'>Faça perguntas em linguagem natural e obtenha respostas direto do seu banco de dados!</p>", unsafe_allow_html=True)


# --- CONFIGURAÇÃO DA SIDEBAR ---
with st.sidebar:
    # st.image("url_do_seu_logo.png", width=100) 
    st.header("⚙️ Configurações")
    st.markdown("---")
    gemini_api_key = st.text_input("🔑 Chave API Gemini", type="password", key="gem_key_sidebar", value=os.getenv("GEMINI_API_KEY", ""))
    MODELO_GEMINI_ESCOLHIDO = st.text_input("🤖 Modelo Gemini", value=os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-latest"), key="gem_model_sidebar")
    if st.button("Listar Modelos Gemini", key="btn_list_models_sidebar", use_container_width=True):
        listar_modelos_disponiveis_no_streamlit(gemini_api_key)
    st.markdown("---")
    st.subheader("📦 Banco de Dados MySQL")
    mysql_host = st.text_input("Host", value=os.getenv("MYSQL_HOST", "localhost"), key="my_host_sidebar")
    mysql_user = st.text_input("Usuário", value=os.getenv("MYSQL_USER", "root"), key="my_user_sidebar")
    mysql_password = st.text_input("Senha", type="password", value=os.getenv("MYSQL_PASSWORD", ""), key="my_pass_sidebar")
    mysql_db_name_input = st.text_input("Nome do Banco", value=os.getenv("MYSQL_DB", "querypilot"), key="my_db_sidebar") # Mudado para querypilot no .env

# --- ESTADO DA SESSÃO ---
if "pergunta" not in st.session_state: st.session_state.pergunta = ""
if "query_sql" not in st.session_state: st.session_state.query_sql = ""
if "resultados_db" not in st.session_state: st.session_state.resultados_db = []

# --- SUGESTÕES DE PERGUNTAS ---
st.subheader("💡 Sugestões de Perguntas")
sugestoes_cols = st.columns(4) 
botoes_sugestao = {
    "📋 Clientes": "Me mostre todos os clientes", "🏠 Endereços": "Quais são os endereços cadastrados",
    "💸 Pagamentos Rec.": "Liste os últimos 5 pagamentos", "📈 Movim. Hoje": "Quais movimentações ocorreram hoje"
}
for i, (texto_botao, pergunta_sugerida) in enumerate(botoes_sugestao.items()):
    if sugestoes_cols[i].button(texto_botao, key=f"btn_sug_{i}_main", use_container_width=True): 
        st.session_state.pergunta = pergunta_sugerida
        st.session_state.query_sql = ""
        st.session_state.resultados_db = []
        # st.experimental_rerun()

# --- PERGUNTA PERSONALIZADA E EXECUÇÃO ---
st.subheader("⌨️ Faça sua Pergunta")
input_layout_cols = st.columns([0.5, 3, 0.5]) # [espaço_esq, conteúdo, espaço_dir]

with input_layout_cols[1]: 
    pergunta_usuario_input = st.text_input(
        " ", 
        value=st.session_state.pergunta,
        key="input_pergunta_main_page", 
        label_visibility="collapsed",
        placeholder="Digite sua pergunta aqui..."
    )

    action_buttons_cols = st.columns(2) # Duas colunas para os botões de ação

    with action_buttons_cols[0]: 
        

        st.markdown('<div class="botao-executar-principal">', unsafe_allow_html=True)
        if st.button("✨ Gerar e Executar", key="btn_exec_main_page", type="primary", use_container_width=True): 
            # ... (lógica do botão de executar como antes) ...
            if pergunta_usuario_input:
                st.session_state.pergunta = pergunta_usuario_input
                if not gemini_api_key: st.error("Chave da API Gemini não fornecida!"); st.stop()
                if not MODELO_GEMINI_ESCOLHIDO: st.error("Nome do Modelo Gemini não especificado!"); st.stop()
                if not all([mysql_host, mysql_user, mysql_db_name_input]): st.error("Configurações do MySQL incompletas!"); st.stop()

                with st.spinner("Obtendo estrutura do banco... ⏳"):
                    estrutura_db = obter_estruturas_tabelas_cached(mysql_host, mysql_user, mysql_password, mysql_db_name_input)
                
                if isinstance(estrutura_db, dict) and estrutura_db.get("error"):
                    st.error(f"Falha ao obter estrutura do banco: {estrutura_db['error']}")
                    st.session_state.query_sql, st.session_state.resultados_db = "", []
                elif not estrutura_db :
                    st.error("Estrutura do banco de dados está vazia. Verifique as configurações ou se o banco possui tabelas.")
                    st.session_state.query_sql, st.session_state.resultados_db = "", []
                else:
                    st.toast("Estrutura do banco obtida.", icon="📄")
                    with st.spinner(f"Gerando SQL com {MODELO_GEMINI_ESCOLHIDO}... 🤖"):
                        st.session_state.query_sql = gerar_query_sql_com_gemini(
                            st.session_state.pergunta, estrutura_db, gemini_api_key, MODELO_GEMINI_ESCOLHIDO, mysql_db_name_input
                        )
                    if st.session_state.query_sql and not st.session_state.query_sql.startswith("Erro"):
                        with st.spinner("Executando SQL no banco..."):
                            _, st.session_state.resultados_db = executar_query_mysql(
                                st.session_state.query_sql, mysql_host, mysql_user, mysql_password, mysql_db_name_input
                            )
                        if isinstance(st.session_state.resultados_db, dict) and st.session_state.resultados_db.get("error"):
                            st.error(f"Erro ao executar query: {st.session_state.resultados_db['error']}")
                            if st.session_state.resultados_db.get("query_com_erro"):
                                 st.code(st.session_state.resultados_db["query_com_erro"], language="sql")
                            st.session_state.resultados_db = [] 
                        else:
                            salvar_historico_db(st.session_state.pergunta, st.session_state.query_sql, st.session_state.resultados_db, mysql_host, mysql_user, mysql_password, mysql_db_name_input)
                    else: 
                        st.error(f"Falha ao gerar SQL: {st.session_state.query_sql if st.session_state.query_sql else 'Nenhuma query foi gerada.'}")
                        st.session_state.resultados_db = []
            else:
                st.warning("Por favor, digite uma pergunta.")
        st.markdown('</div>', unsafe_allow_html=True)

    with action_buttons_cols[1]:
        # O botão Limpar Busca usará o estilo padrão de .stButton>button do style.css
        if st.button("🧹 Limpar Busca", key="btn_limpar_busca_main", type="search" use_container_width=True):
            st.session_state.pergunta = ""
            st.session_state.query_sql = ""
            st.session_state.resultados_db = []
            # st.experimental_rerun()

# --- EXIBIÇÃO DE RESULTADOS E FEEDBACK ---
# ... (Restante da sua seção de exibição de resultados e feedback, como antes) ...
if st.session_state.query_sql and not st.session_state.query_sql.startswith("Erro"): 
    st.markdown("---")
    container_resultados = st.container(border=True) 
    with container_resultados:
        st.subheader("🔍 Resultados da Consulta")
        if st.toggle("👁️ Mostrar Consulta SQL Gerada", value=True, key="toggle_sql_disp_main"): 
            st.code(st.session_state.query_sql, language="sql")

        if st.session_state.resultados_db:
            if isinstance(st.session_state.resultados_db, dict) and "status" in st.session_state.resultados_db :
                 st.success(f"{st.session_state.resultados_db['status']}. Linhas afetadas: {st.session_state.resultados_db.get('linhas_afetadas', 'N/A')}")
            elif isinstance(st.session_state.resultados_db, list) and len(st.session_state.resultados_db) > 0:
                st.success(f"✅ Consulta realizada! {len(st.session_state.resultados_db)} linha(s) retornada(s).")
                st.dataframe(st.session_state.resultados_db, use_container_width=True, hide_index=True)
            elif isinstance(st.session_state.resultados_db, list) and len(st.session_state.resultados_db) == 0: 
                st.info("ℹ️ A consulta SQL foi executada, mas não retornou dados.")
        elif isinstance(st.session_state.resultados_db, dict) and st.session_state.resultados_db.get("error"):
            pass # O erro já foi mostrado na lógica de execução
        elif st.session_state.query_sql.strip().upper().startswith("SELECT"): 
            st.info("ℹ️ A consulta SQL foi executada, mas não retornou dados (ou erro na execução).")
        
        st.markdown("---")
        st.subheader("⭐ Feedback")
        feedback_key = f"fb_radio_main_{hash(st.session_state.pergunta)}_{hash(st.session_state.query_sql)}"
        feedback_selecionado = st.radio(
            "A resposta foi útil?", ("👍 Sim", "👎 Não"), index=None, key=feedback_key, horizontal=True
        )
        if feedback_selecionado:
            salvar_feedback_db(st.session_state.pergunta, feedback_selecionado, mysql_host, mysql_user, mysql_password, mysql_db_name_input)
            st.toast(f"Obrigado pelo seu feedback: '{feedback_selecionado}'!", icon="🙌")

# --- RODAPÉ ---
st.markdown("---")
footer_cols = st.columns([1,2,1])
with footer_cols[1]:
    st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #718096;'>Desenvolvido com Streamlit e Gemini AI</p>", unsafe_allow_html=True)