import argparse
from pathlib import Path
from docling.document_converter import DocumentConverter
from config import CONFIG

# === Configuration ===
INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/result/markdown")
OVERWRITE = False

# === Initialize the converter ===
converter = DocumentConverter()


def convert_file(input_path: Path, output_path: Path):
    try:
        result = converter.convert(input_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result.document.export_to_markdown(), encoding="utf-8")
        print(f"✅ Converted: {input_path} → {output_path}")
    except Exception as e:
        print(f"❌ Failed to convert {input_path}: {e}")


def convert_directory(input_dir: Path, output_dir: Path, supported_exts: list[str]):
    for file_path in input_dir.rglob("*"):
        if file_path.suffix.lower() not in supported_exts:
            print(file_path)
            print(f"❌ Unsupported file type: {file_path.suffix}")
            continue

        rel_path = file_path.relative_to(input_dir).with_suffix(".md")
        output_path = output_dir / rel_path

        if output_path.exists() and not OVERWRITE:
            print(f"⏩ Skipping: {output_path}")
            continue

        try:
            convert_file(file_path, output_path)
        except Exception as e:
            print(f"❌ Failed to convert {file_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert documents to Markdown using Docling."
    )
    parser.add_argument(
        "--ext",
        nargs="+",
        default=[".docx"],
        help="List of supported file extensions (e.g. --ext .docx .pdf)",
    )
    args = parser.parse_args()

    # Normalize extensions
    supported_exts = [
        ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in args.ext
    ]

    convert_directory(INPUT_DIR, OUTPUT_DIR, supported_exts)
