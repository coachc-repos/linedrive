#!/usr/bin/env python3
"""
Add HeyGen section from markdown file to Word document
This script reads the HeyGen section from a markdown file and appends it to the Word document
"""

from console_ui.word_processing import convert_markdown_to_word
import sys
from pathlib import Path
import asyncio

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "console_ui"))


async def add_heygen_to_word(md_file_path: str):
    """Add HeyGen section from markdown to Word document"""

    md_path = Path(md_file_path)

    if not md_path.exists():
        print(f"❌ Markdown file not found: {md_path}")
        return

    # Read the markdown file
    print(f"📄 Reading markdown file: {md_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if HeyGen section exists
    if "# 🎬 HEYGEN READY SCRIPT" not in content:
        print("❌ No HeyGen section found in markdown file")
        return

    print("✅ HeyGen section found in markdown")

    # Find the corresponding Word document
    word_path = md_path.with_suffix('.docx')

    if not word_path.exists():
        print(f"❌ Word document not found: {word_path}")
        return

    print(f"📘 Found Word document: {word_path}")

    # Get file sizes before
    md_size = md_path.stat().st_size
    word_size_before = word_path.stat().st_size

    print(f"📊 Markdown size: {md_size:,} bytes")
    print(f"📊 Word size (before): {word_size_before:,} bytes")

    # Recreate Word document with full content
    print(f"🔄 Recreating Word document with full content...")
    await convert_markdown_to_word(content, word_path, "")

    # Get file size after
    word_size_after = word_path.stat().st_size

    print(f"📊 Word size (after): {word_size_after:,} bytes")
    print(f"📈 Size increase: {word_size_after - word_size_before:,} bytes")

    if word_size_after > word_size_before:
        print(f"✅ Word document updated successfully!")
        print(f"📘 Updated file: {word_path}")
    else:
        print(f"⚠️ Word document size didn't increase - may not have updated correctly")


async def main():
    """Main function"""
    print("🎬 HeyGen Section → Word Document Updater")
    print("=" * 60)

    if len(sys.argv) > 1:
        # File path provided as argument
        md_file = sys.argv[1]
    else:
        # Find most recent markdown file in Dev/Scripts
        scripts_dir = Path.home() / "Dev/Scripts"

        if not scripts_dir.exists():
            print(f"❌ Scripts directory not found: {scripts_dir}")
            return

        # Find most recent .md file
        md_files = sorted(scripts_dir.glob("*.md"),
                          key=lambda p: p.stat().st_mtime, reverse=True)

        if not md_files:
            print(f"❌ No markdown files found in {scripts_dir}")
            return

        # Show recent files and let user choose
        print("\n📁 Recent markdown files:")
        for i, md_file in enumerate(md_files[:10], 1):
            mtime = md_file.stat().st_mtime
            from datetime import datetime
            time_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            print(f"{i}. {md_file.name} ({time_str})")

        print("\n0. Cancel")

        try:
            choice = input(
                "\n👆 Select file (or press Enter for most recent): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Cancelled")
            return

        if choice == "0":
            print("❌ Cancelled")
            return
        elif choice == "" or choice == "1":
            md_file = str(md_files[0])
        elif choice.isdigit() and 1 <= int(choice) <= len(md_files):
            md_file = str(md_files[int(choice) - 1])
        else:
            print("❌ Invalid selection")
            return

    await add_heygen_to_word(md_file)


if __name__ == "__main__":
    asyncio.run(main())
