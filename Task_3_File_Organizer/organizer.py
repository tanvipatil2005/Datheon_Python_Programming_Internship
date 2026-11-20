import os
import shutil
from pathlib import Path

# Extension-to-category folder mapping
EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".xlsx": "Documents",
    ".xls": "Documents",
    ".csv": "Documents",
    ".pptx": "Documents",
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".svg": "Images",
    ".webp": "Images",
    # Videos
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".mov": "Videos",
    ".avi": "Videos",
    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    # Code
    ".py": "Code",
    ".js": "Code",
    ".html": "Code",
    ".css": "Code",
    ".java": "Code",
    ".cpp": "Code",
    ".c": "Code",
    ".json": "Code",
    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".aac": "Audio"
}

def create_sample_messy_folder(base_dir="sample_downloads"):
    """Creates a safe sandbox folder with dummy files for testing the organizer."""
    target = Path(base_dir)
    target.mkdir(exist_ok=True)
    sample_files = [
        "internship_offer.pdf",
        "lecture_notes.docx",
        "budget_2026.xlsx",
        "profile_pic.jpg",
        "screenshot_ui.png",
        "demo_recording.mp4",
        "project_backup.zip",
        "helper_script.py",
        "index.html",
        "unknown_file.xyz"
    ]
    for filename in sample_files:
        file_path = target / filename
        if not file_path.exists():
            file_path.write_text(f"Sample content for {filename}", encoding="utf-8")
    return target.resolve()

def get_unique_destination(dest_folder, filename):
    """Prevents overwriting by appending _1, _2, etc. if a filename collision occurs."""
    dest_path = dest_folder / filename
    if not dest_path.exists():
        return dest_path

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_folder / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1

def organize_directory(target_dir):
    """Scans target_dir, creates category folders, and safely relocates files."""
    target_path = Path(target_dir).resolve()
    script_path = Path(__file__).resolve()

    if not target_path.exists() or not target_path.is_dir():
        print(f"Error: '{target_path}' is not a valid directory.")
        return

    summary_counts = {}
    total_moved = 0
    errors = 0

    print("\n" + "=" * 60)
    print(f"ORGANIZING DIRECTORY: {target_path}")
    print("=" * 60)

    try:
        with os.scandir(target_path) as entries:
            for entry in entries:
                # Skip directories and skip the organizer.py script itself
                if not entry.is_file():
                    continue
                entry_path = Path(entry.path).resolve()
                if entry_path == script_path:
                    continue

                ext = entry_path.suffix.lower()
                category = EXTENSION_MAP.get(ext, "Others")
                category_folder = target_path / category

                try:
                    category_folder.mkdir(exist_ok=True)
                    destination = get_unique_destination(category_folder, entry.name)
                    shutil.move(str(entry_path), str(destination))

                    summary_counts[category] = summary_counts.get(category, 0) + 1
                    total_moved += 1
                    print(f"[MOVED] {entry.name:<25} -> /{category}/{destination.name}")

                except (FileExistsError, PermissionError, OSError) as err:
                    errors += 1
                    print(f"[ERROR] Could not move '{entry.name}': {err}")

    except PermissionError as err:
        print(f"Permission denied accessing directory: {err}")
        return

    # Execution summary
    print("\n" + "=" * 60)
    print("                 EXECUTION SUMMARY")
    print("=" * 60)
    if total_moved == 0:
        print("No loose files needed organizing.")
    else:
        for category, count in sorted(summary_counts.items()):
            print(f"  /{category:<15}: {count} file(s) moved")
    print("-" * 60)
    print(f"Total Files Relocated : {total_moved}")
    print(f"Errors Encountered    : {errors}")
    print("=" * 60)

def main():
    print("=" * 60)
    print("       AUTOMATED FILE ORGANIZER & CLEANUP UTILITY")
    print("=" * 60)
    print("1. Test safely with an auto-generated 'sample_downloads' folder")
    print("2. Enter a custom folder path to organize")

    choice = input("\nSelect an option (1 or 2): ").strip()

    if choice == "1":
        folder_to_clean = create_sample_messy_folder()
        print(f"\nCreated test files inside: {folder_to_clean}")
        organize_directory(folder_to_clean)
    elif choice == "2":
        custom_path = input("Enter full directory path: ").strip().strip('"')
        organize_directory(custom_path)
    else:
        print("Invalid choice. Please run the script again and select 1 or 2.")

if __name__ == "__main__":
    main()