"""
main.py
-------
Entry point for the Image-to-CSV Data Extraction System.

Usage:
    python main.py --input ./input_images/ --config ./config/fields.json
    python main.py --input card1.jpg --config ./config/fields.json --format excel
    python main.py --input ./input_images/ --fields name age blood_group
"""

import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from modules.image_loader import (
    load_images_from_folder,
    load_single_image,
    preprocess_image
)
from modules.extractor import batch_extract
from modules.exporter import export_data, print_preview

# Load environment variables from .env file
load_dotenv()

console = Console()


def print_banner():
    text = Text()
    text.append("🩸 Image-to-CSV Extractor\n", style="bold red")
    text.append("Extract structured data from card images → CSV / Excel", style="dim")
    console.print(Panel(text, border_style="red"))


def load_config(config_path: str) -> dict:
    """Loads field configuration from a JSON file."""
    path = Path(config_path)
    if not path.exists():
        console.print(f"[red]❌ Config file not found:[/red] {config_path}")
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(path) as f:
        config = json.load(f)

    console.print(f"[green]✅ Config loaded:[/green] {config_path}")
    console.print(f"   Fields  : [cyan]{', '.join(config['fields'])}[/cyan]")
    console.print(f"   Format  : [cyan]{config['output_format']}[/cyan]")
    console.print(f"   Output  : [cyan]{config['output_file']}[/cyan]\n")

    return config


def check_api_key():
    """Verifies the Anthropic API key is set."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        console.print("[bold red]❌ ANTHROPIC_API_KEY is not set![/bold red]")
        console.print("  1. Copy [cyan].env.example[/cyan] → [cyan].env[/cyan]")
        console.print("  2. Add your API key from [link]https://console.anthropic.com[/link]")
        raise EnvironmentError("Missing ANTHROPIC_API_KEY")
    console.print("[green]✅ API key found.[/green]")


def main():
    print_banner()

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="Extract structured data from card images into CSV/Excel"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to an image file OR a folder of images"
    )
    parser.add_argument(
        "--config", default="./config/fields.json",
        help="Path to the fields config JSON (default: ./config/fields.json)"
    )
    parser.add_argument(
        "--fields", nargs="+",
        help="Override config fields. E.g.: --fields name age blood_group"
    )
    parser.add_argument(
        "--format", choices=["csv", "excel"], default=None,
        help="Override output format from config: csv or excel"
    )
    parser.add_argument(
        "--output-dir", default="./output",
        help="Directory to save output files (default: ./output)"
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="Print a preview of extracted data before saving"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Save preprocessed images for debugging"
    )

    args = parser.parse_args()

    # --- Validate API Key ---
    check_api_key()

    # --- Load Config ---
    config = load_config(args.config)

    # Override fields if provided via CLI
    fields = args.fields if args.fields else config["fields"]
    output_format = args.format if args.format else config.get("output_format", "csv")
    output_file = config.get("output_file", "output")

    # --- Load Images ---
    input_path = Path(args.input)
    if input_path.is_dir():
        image_list = load_images_from_folder(str(input_path))
    else:
        single = load_single_image(str(input_path))
        image_list = [single] if single else []

    if not image_list:
        console.print("[red]❌ No valid images found. Exiting.[/red]")
        return

    # --- Preprocess Images ---
    console.print(f"\n[bold]🖼️  Preprocessing {len(image_list)} image(s)...[/bold]")
    image_records = []
    for img in image_list:
        b64 = preprocess_image(img["path"], save_debug=args.debug)
        if b64:
            image_records.append({
                "filename": img["filename"],
                "path": img["path"],
                "base64": b64
            })

    # --- Extract Data ---
    results = batch_extract(image_records, fields)

    # --- Preview ---
    if args.preview:
        print_preview(results, fields)

    # --- Export ---
    export_data(
        records=results,
        fields=fields,
        output_dir=args.output_dir,
        output_file=output_file,
        output_format=output_format
    )

    console.print("\n[bold green]🎉 Done! All images processed successfully.[/bold green]")


if __name__ == "__main__":
    main()
