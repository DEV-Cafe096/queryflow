from google import genai
from google.genai import types

from app.config import get_settings
from app.llm.prompt_templates import build_prompt
from app.models.schemas import Dialect


class GeminiError(Exception):
    pass


def _client(api_key: str | None = None) -> genai.Client:
    key = api_key or get_settings().gemini_api_key
    if not key:
        raise GeminiError("Chave de API do Gemini não configurada.")
    return genai.Client(api_key=key)


def generate_sql(
    question: str,
    schema: dict,
    dialect: Dialect,
    api_key: str | None = None,
    model_name: str | None = None,
) -> str:
    if not schema:
        raise GeminiError("Estrutura do banco de dados está vazia ou não pôde ser carregada.")

    client = _client(api_key)
    model = model_name or get_settings().gemini_model_name
    prompt = build_prompt(question, dialect, schema)

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.05, max_output_tokens=2048),
        )
    except Exception as exc:
        raise GeminiError(f"Falha ao chamar a API do Gemini: {exc}") from exc

    query = (response.text or "").strip()
    query = query.replace("```sql", "").replace("```", "").strip()
    if not query:
        raise GeminiError("O Gemini retornou uma resposta vazia.")
    return query


def list_models(api_key: str | None = None) -> list[str]:
    client = _client(api_key)
    names = []
    for model in client.models.list():
        actions = getattr(model, "supported_actions", None) or []
        if not actions or "generateContent" in actions:
            names.append(model.name)
    return names
