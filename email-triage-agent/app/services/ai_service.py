import json
import re
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError
from app.core.config import settings

client = InferenceClient(api_key=settings.huggingface_api_key)

# Orden de prioridad: si el primero falla (rate limit, indisponible, JSON invalido),
# se intenta con el siguiente
MODEL_FALLBACK_CHAIN = [
    "Qwen/Qwen2.5-72B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "HuggingFaceH4/zephyr-7b-beta",
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
    # Intento 1: parsear directo
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        pass

    # Intento 2: buscar el primer '{' y el ultimo '}' del texto
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
            print(f"Intentando con modelo: {model_name}")
            response = client.chat_completion(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2,  # baja temperatura: queremos consistencia, no creatividad
            )
            raw_text = response.choices[0].message.content
            result = _extract_json(raw_text)
            result = _validate_result(result)

            print(f"Exito con modelo: {model_name}")
            return result

        except HfHubHTTPError as e:
            print(f"Fallo {model_name} (HTTP/rate limit): {e}")
            last_error = e
            continue
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Fallo {model_name} (JSON invalido): {e}")
            last_error = e
            continue

    raise RuntimeError(f"Todos los modelos fallaron. Ultimo error: {last_error}")