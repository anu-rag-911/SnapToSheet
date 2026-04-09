"""
extractor.py
------------
Uses Google Gemini Vision API (FREE) to extract structured data
from card images based on dynamic user-defined fields.

Free Tier: 1,500 requests/day | 15 requests/minute
Get API key: https://aistudio.google.com
"""

import os
import json
import base64
from google import genai
from google.genai import types
from PIL import Image
import io
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()
console = Console()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    console.print("[red]❌ GEMINI_API_KEY not found in .env file![/red]")
    console.print("   Get your free key at: [cyan]https://aistudio.google.com[/cyan]")
    client = None
else:
    client = genai.Client(api_key=GEMINI_API_KEY)


def build_extraction_prompt(fields: list[str]) -> str:
    """Dynamically builds extraction prompt from user-defined fields."""
    field_list = ", ".join(f'"{f}"' for f in fields)
    fields_json_example = {f: "..." for f in fields}

    return f"""
You are a data extraction assistant. Carefully examine the card image provided.

Extract ONLY the following fields: {field_list}

Rules:
- Return ONLY a valid JSON object with exactly these keys: {field_list}
- If a field is not found or unclear in the image, set its value to null
- Do NOT add extra fields, comments, or any explanation outside the JSON
- For names: use proper capitalization (e.g. "Ram Bahadur Thapa")
- For blood_group: use standard notation (A+, B-, O+, AB+, etc.)
- For sex/gender: use "Male", "Female", or "Other"
- For age: return as a number string (e.g. "28")

Expected output format:
{json.dumps(fields_json_example, indent=2)}

Return ONLY the JSON object. No markdown, no code fences, no explanation.
""".strip()


def base64_to_pil(base64_image: str) -> Image.Image:
    """Converts a base64 string back to a PIL Image."""
    image_bytes = base64.b64decode(base64_image)
    return Image.open(io.BytesIO(image_bytes))


def extract_from_image(base64_image: str, fields: list[str], filename: str = "") -> dict:
    """
    Sends an image to Gemini Vision and extracts the specified fields.

    Returns a dict like: {"name": "Ram Bahadur", "age": "28", "blood_group": "O+", ...}
    """
    label = filename or "image"
    console.print(f"[cyan]🔍 Extracting from:[/cyan] {label}")

    if not client:
        console.print("[red]  ❌ Gemini client not initialized. Check your API key.[/red]")
        return {field: None for field in fields}

    prompt = build_extraction_prompt(fields)

    try:
        pil_image = base64_to_pil(base64_image)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, pil_image],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=500,
            )
        )

        raw_text = response.text.strip()

        # Strip markdown code fences if model adds them
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            raw_text = "\n".join(lines).strip()

        extracted = json.loads(raw_text)

        # Fill any missing fields with None
        for field in fields:
            if field not in extracted:
                extracted[field] = None

        console.print(f"[green]  ✅ Success:[/green] {label}")
        return extracted

    except json.JSONDecodeError as e:
        console.print(f"[red]  ❌ JSON parse error for {label}:[/red] {e}")
        return {field: None for field in fields}

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg or "api key" in error_msg.lower():
            console.print("[red]  ❌ Invalid API key![/red] Check GEMINI_API_KEY in .env")
        elif "quota" in error_msg.lower() or "429" in error_msg:
            console.print("[red]  ❌ Rate limit hit![/red] Wait 1 min (Free: 15 req/min)")
        elif "SAFETY" in error_msg:
            console.print(f"[yellow]  ⚠️  Safety filter blocked:[/yellow] {label}")
        else:
            console.print(f"[red]  ❌ Error for {label}:[/red] {error_msg}")
        return {field: None for field in fields}


def batch_extract(image_records: list[dict], fields: list[str]) -> list[dict]:
    """Processes multiple images and extracts data from each."""
    import time

    results = []
    total = len(image_records)

    console.print(f"\n[bold cyan]📦 Processing {total} image(s) with Gemini Vision...[/bold cyan]")
    console.print("[dim]   Free tier: 15 req/min. Auto-pause applied if needed.[/dim]\n")

    for i, record in enumerate(image_records, 1):
        console.print(f"[dim]({i}/{total})[/dim]", end=" ")

        data = extract_from_image(
            base64_image=record["base64"],
            fields=fields,
            filename=record["filename"]
        )
        data["_source_file"] = record["filename"]
        results.append(data)

        # Auto rate-limit pause every 14 requests (free tier = 15/min)
        if i % 14 == 0 and i < total:
            console.print(f"\n[yellow]⏳ Pausing 60s for rate limit after {i} requests...[/yellow]")
            time.sleep(60)

    console.print(f"\n[bold green]✅ Done! {len(results)}/{total} images processed.[/bold green]")
    return results
