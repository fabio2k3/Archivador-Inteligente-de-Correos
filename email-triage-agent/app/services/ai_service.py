import json
import logging
import re
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError
from app.core.config import settings

logger = logging.getLogger(__name__)

client = InferenceClient(api_key=settings.huggingface_api_key)

MODEL_FALLBACK_CHAIN = [
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.3-70B-Instruct",
    "deepseek-ai/DeepSeek-V3-0324",
]


def _build_prompt(subject: str, sender: str, body: str) -> str:
    return f"""Analiza el siguiente correo electronico y responde UNICAMENTE con un objeto JSON valido, sin texto adicional, sin markdown, sin explicaciones.

El JSON debe tener EXACTAMENTE esta forma:
{{
  "summary_bullets": ["viñeta 1", "viñeta 2", "viñeta 3"],
  "due_date": "YYYY-MM-DD o null si no aplica",
  "suggested_category": "importante" | "newsletter" | "spam" | "sin_clasificar"
}}

Correo a analizar:
De: {sender}
Asunto: {subject}
Cuerpo:
{body}

Responde solo con el JSON, nada mas."""


def _extract_json(raw_text: str) -> dict:
    """
    Los modelos open-source a veces envuelven el JSON en markdown (```json ... ```)
    o agregan texto antes/despues. Esta funcion extrae el bloque JSON de forma robusta.
    """
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError(f"No se pudo extraer JSON valido de la respuesta: {raw_text[:200]}")


def _validate_result(data: dict) -> dict:
    """Verifica que el JSON tenga la forma esperada antes de aceptarlo como valido."""
    if "summary_bullets" not in data or len(data["summary_bullets"]) != 3:
        raise ValueError("summary_bullets debe tener exactamente 3 elementos")

    valid_categories = {"importante", "newsletter", "spam", "sin_clasificar"}
    if data.get("suggested_category") not in valid_categories:
        raise ValueError(f"Categoria invalida: {data.get('suggested_category')}")

    return data


def analyze_email(subject: str, sender: str, body: str) -> dict:
    prompt = _build_prompt(subject, sender, body)
    last_error = None

    for model_name in MODEL_FALLBACK_CHAIN:
        try:
            logger.info(f"Intentando con modelo: {model_name}")
            response = client.chat_completion(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2,
            )
            raw_text = response.choices[0].message.content
            result = _extract_json(raw_text)
            result = _validate_result(result)

            logger.info(f"Exito con modelo: {model_name}")
            return result

        except HfHubHTTPError as e:
            logger.warning(f"Fallo {model_name} (HTTP/rate limit): {e}")
            last_error = e
            continue
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"Fallo {model_name} (JSON invalido): {e}")
            last_error = e
            continue

    logger.error(f"Todos los modelos fallaron para el correo '{subject}'. Ultimo error: {last_error}")
    raise RuntimeError(f"Todos los modelos fallaron. Ultimo error: {last_error}")