"""
test_setup.py
-------------
Verifies that all dependencies and modules are correctly installed.
Run this after installing requirements.txt to confirm Phase 1 is complete.

Usage:
    python tests/test_setup.py
"""

import sys
from rich.console import Console
from rich.table import Table

console = Console()

def check_import(module_name: str, import_as: str = None, version_attr: str = "__version__"):
    """Tries to import a module and returns (success, version)."""
    try:
        import importlib
        mod = importlib.import_module(import_as or module_name)
        version = getattr(mod, version_attr, "installed")
        return True, version
    except ImportError:
        return False, "NOT FOUND"


def run_checks():
    console.print("\n[bold cyan]🔍 Phase 1 — Setup Verification[/bold cyan]\n")

    checks = [
        ("anthropic",      "anthropic",     "Python SDK for Claude API"),
        ("pandas",         "pandas",        "Data handling & DataFrame"),
        ("PIL",            "PIL",           "Image processing (Pillow)"),
        ("cv2",            "cv2",           "Image preprocessing (OpenCV)"),
        ("openpyxl",       "openpyxl",      "Excel file export"),
        ("easyocr",        "easyocr",       "OCR fallback engine"),
        ("rich",           "rich",          "Terminal UI & pretty output"),
        ("dotenv",         "dotenv",        "Environment variable loader"),
    ]

    table = Table(title="Dependency Check", show_lines=True)
    table.add_column("Library",     style="cyan",  no_wrap=True)
    table.add_column("Status",      style="bold",  no_wrap=True)
    table.add_column("Version",     style="dim")
    table.add_column("Purpose",     style="white")

    all_passed = True
    for module, import_name, purpose in checks:
        ok, version = check_import(import_name)
        status = "[green]✅ OK[/green]" if ok else "[red]❌ MISSING[/red]"
        if not ok:
            all_passed = False
        table.add_row(module, status, str(version), purpose)

    console.print(table)

    # Check project modules
    console.print("\n[bold]📂 Checking Project Modules...[/bold]")
    project_modules = [
        ("modules.image_loader", "Image loading & preprocessing"),
        ("modules.extractor",    "Claude Vision extraction"),
        ("modules.exporter",     "CSV / Excel export"),
    ]

    for mod_path, purpose in project_modules:
        try:
            import importlib
            importlib.import_module(mod_path)
            console.print(f"  [green]✅[/green] {mod_path:<30} [dim]{purpose}[/dim]")
        except ImportError as e:
            console.print(f"  [red]❌[/red] {mod_path:<30} [dim]{e}[/dim]")
            all_passed = False

    # Check folder structure
    import os
    console.print("\n[bold]📁 Checking Folder Structure...[/bold]")
    folders = ["config", "modules", "input_images", "output", "tests"]
    for folder in folders:
        exists = os.path.isdir(folder)
        icon = "[green]✅[/green]" if exists else "[red]❌[/red]"
        console.print(f"  {icon} ./{folder}/")

    # Check config
    console.print("\n[bold]⚙️  Checking Config...[/bold]")
    import json
    config_path = "config/fields.json"
    try:
        with open(config_path) as f:
            config = json.load(f)
        console.print(f"  [green]✅[/green] {config_path}")
        console.print(f"     Fields: [cyan]{', '.join(config['fields'])}[/cyan]")
    except Exception as e:
        console.print(f"  [red]❌[/red] {config_path}: {e}")
        all_passed = False

    # Check API key
    console.print("\n[bold]🔑 Checking API Key...[/bold]")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if api_key and api_key != "your_api_key_here":
            console.print("  [green]✅[/green] ANTHROPIC_API_KEY is set.")
        else:
            console.print("  [yellow]⚠️  ANTHROPIC_API_KEY not set.[/yellow]")
            console.print("     → Copy [cyan].env.example[/cyan] to [cyan].env[/cyan] and add your key.")
    except Exception as e:
        console.print(f"  [red]❌[/red] Could not check API key: {e}")

    # Summary
    console.print()
    if all_passed:
        console.print("[bold green]🎉 Phase 1 Complete! All checks passed.[/bold green]")
        console.print("[dim]   You're ready to start Phase 2.[/dim]\n")
    else:
        console.print("[bold red]⚠️  Some checks failed. Run:[/bold red]")
        console.print("   [cyan]pip install -r requirements.txt[/cyan]\n")
        sys.exit(1)


if __name__ == "__main__":
    # Run from project root: python tests/test_setup.py
    sys.path.insert(0, ".")
    run_checks()
