import base64

from pydantic import ValidationError

from app.core.config import get_settings
from app.core.errors import ExternalServiceError
from app.schemas.ai import NutritionExtraction
from app.services.openai_client import extract_json_object, get_client

settings = get_settings()

_PROMPT = """You are a nutrition-label and food-photo analyzer for a calorie tracking app.
Look at the attached image (it may be a packaged food's nutrition facts label, or a photo of a \
plate of food) and estimate its nutritional content.

Respond with ONLY a single JSON object, no prose, no markdown fences, matching exactly this shape:
{
  "food_name": string,
  "quantity": number,
  "unit": string (e.g. "serving", "g", "plate"),
  "calories": number,
  "protein_g": number,
  "carbs_g": number,
  "fat_g": number,
  "micros": { "<vitamin or mineral name>": number, ... },
  "confidence_note": string (one short sentence noting any assumptions or uncertainty)
}

If the image is a printed nutrition label, read the values directly. If it's a photo of a meal, \
give your best estimate based on typical portion sizes and visible ingredients."""


def extract_nutrition_from_image(image_bytes: bytes, media_type: str) -> NutritionExtraction:
    client = get_client()
    encoded = base64.standard_b64encode(image_bytes).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{media_type};base64,{encoded}"},
                        },
                    ],
                }
            ],
        )
    except Exception as exc:  # network/SDK errors from the OpenAI API
        raise ExternalServiceError(f"AI image analysis failed: {exc}") from exc

    text = response.choices[0].message.content or ""
    data = extract_json_object(text)

    try:
        return NutritionExtraction.model_validate(data)
    except ValidationError as exc:
        raise ExternalServiceError(f"AI response did not match the expected shape: {exc}") from exc
