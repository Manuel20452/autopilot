"""
AutoPilot — File & Data Automation Toolkit
Automates repetitive file operations, data cleaning, and report generation.
Author: Manuel | GitHub: Manuel20452
"""

import os
import sys
import csv
import json
import shutil
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from collections import Counter


class FileOrganizer:
    """Automatically organize files into categorized folders."""

    CATEGORIES = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xlsx", ".xls", ".pptx", ".csv"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".sh", ".rb", ".go", ".rs", ".php"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "Executables": [".exe", ".msi", ".deb", ".rpm", ".AppImage", ".bin"],
    }

    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.log = []

    def organize(self, dry_run=False):
        """
        Sort files into category folders.
        
        Args:
            dry_run: If True, only show what would happen without moving files
            
        Returns:
            List of actions taken
        """
        if not self.source_dir.exists():
            print(f"[!] Directory not found: {self.source_dir}")
            return []

        print(f"\n📁 Organizing: {self.source_dir}")
        print(f"   Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE'}\n")

        files = [f for f in self.source_dir.iterdir() if f.is_file()]
        moved = 0

        for file in files:
            ext = file.suffix.lower()
            category = self._get_category(ext)
            dest_dir = self.source_dir / category

            action = f"  {file.name} → {category}/"
            self.log.append(action)
            print(action)

            if not dry_run:
                dest_dir.mkdir(exist_ok=True)
                dest_path = dest_dir / file.name

                # Handle duplicates
                if dest_path.exists():
                    stem = file.stem
                    dest_path = dest_dir / f"{stem}_{datetime.now().strftime('%H%M%S')}{ext}"

                shutil.move(str(file), str(dest_path))
                moved += 1

        print(f"\n[✓] {'Would move' if dry_run else 'Moved'} {moved}/{len(files)} files")
        return self.log

    def _get_category(self, ext):
        """Determine file category based on extension."""
        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category
        return "Other"


class DuplicateFinder:
    """Find and optionally remove duplicate files using hash comparison."""

    def __init__(self, directory):
        self.directory = Path(directory)

    def find_duplicates(self):
        """
        Find duplicate files by comparing MD5 hashes.
        
        Returns:
            Dict of {hash: [list of file paths]}
        """
        print(f"\n🔍 Scanning for duplicates in: {self.directory}\n")

        hash_map = {}
        file_count = 0

        for file in self.directory.rglob("*"):
            if file.is_file():
                file_count += 1
                file_hash = self._hash_file(file)

                if file_hash in hash_map:
                    hash_map[file_hash].append(str(file))
                else:
                    hash_map[file_hash] = [str(file)]

        duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}

        print(f"  Scanned: {file_count} files")
        print(f"  Duplicates found: {len(duplicates)} groups\n")

        for hash_val, paths in duplicates.items():
            size = os.path.getsize(paths[0])
            print(f"  📄 {self._format_size(size)} — {len(paths)} copies:")
            for p in paths:
                print(f"     {p}")
            print()

        total_waste = sum(
            os.path.getsize(paths[1]) * (len(paths) - 1)
            for paths in duplicates.values()
        )
        print(f"  💾 Space wasted by duplicates: {self._format_size(total_waste)}")

        return duplicates

    def remove_duplicates(self, duplicates, keep="first"):
        """Remove duplicate files, keeping the first or last occurrence."""
        removed = 0
        for paths in duplicates.values():
            to_remove = paths[1:] if keep == "first" else paths[:-1]
            for path in to_remove:
                os.remove(path)
                print(f"  🗑️ Removed: {path}")
                removed += 1
        print(f"\n[✓] Removed {removed} duplicate files")

    def _hash_file(self, filepath, chunk_size=8192):
        """Calculate MD5 hash of a file."""
        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _format_size(self, size):
        """Format bytes to human-readable size."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class DataCleaner:
    """Clean and transform CSV/JSON data files."""

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.data = []
        self._load()

    def _load(self):
        """Load data from CSV or JSON."""
        ext = self.filepath.suffix.lower()

        if ext == ".csv":
            with open(self.filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
        elif ext == ".json":
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            print(f"[!] Unsupported format: {ext}")
            return

        print(f"\n📊 Loaded {len(self.data)} records from {self.filepath.name}")

    def remove_duplicates(self):
        """Remove duplicate rows."""
        before = len(self.data)
        seen = set()
        unique = []

        for row in self.data:
            key = json.dumps(row, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique.append(row)

        self.data = unique
        removed = before - len(self.data)
        print(f"  [✓] Removed {removed} duplicate rows ({len(self.data)} remaining)")
        return self

    def remove_empty(self, columns=None):
        """Remove rows with empty values in specified columns."""
        before = len(self.data)

        if columns:
            self.data = [
                row for row in self.data
                if all(row.get(col, "").strip() for col in columns)
            ]
        else:
            self.data = [
                row for row in self.data
                if all(str(v).strip() for v in row.values())
            ]

        removed = before - len(self.data)
        print(f"  [✓] Removed {removed} rows with empty values")
        return self

    def strip_whitespace(self):
        """Strip leading/trailing whitespace from all values."""
        for row in self.data:
            for key in row:
                if isinstance(row[key], str):
                    row[key] = row[key].strip()
        print(f"  [✓] Stripped whitespace from all fields")
        return self

    def rename_columns(self, mapping):
        """
        Rename columns.
        
        Args:
            mapping: Dict of {old_name: new_name}
        """
        self.data = [
            {mapping.get(k, k): v for k, v in row.items()}
            for row in self.data
        ]
        print(f"  [✓] Renamed {len(mapping)} columns")
        return self

    def filter_rows(self, column, condition):
        """
        Filter rows by a condition.
        
        Args:
            column: Column to filter on
            condition: Lambda function for filtering
        """
        before = len(self.data)
        self.data = [row for row in self.data if condition(row.get(column, ""))]
        print(f"  [✓] Filtered: {before} → {len(self.data)} rows")
        return self

    def summary(self):
        """Print a summary of the data."""
        if not self.data:
            print("  [!] No data to summarize")
            return self

        columns = list(self.data[0].keys())
        print(f"\n  {'='*50}")
        print(f"  DATA SUMMARY")
        print(f"  {'='*50}")
        print(f"  Rows: {len(self.data)}")
        print(f"  Columns: {len(columns)}")
        print(f"  Column names: {', '.join(columns)}")
        print(f"  {'='*50}")
        return self

    def export(self, output_path=None, fmt=None):
        """Export cleaned data to CSV or JSON."""
        if output_path is None:
            stem = self.filepath.stem
            ext = fmt or self.filepath.suffix
            output_path = self.filepath.parent / f"{stem}_cleaned{ext}"

        output_path = Path(output_path)
        ext = output_path.suffix.lower()

        if ext == ".csv":
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                if self.data:
                    writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.data)
        elif ext == ".json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)

        print(f"\n  [✓] Exported to: {output_path}")
        return str(output_path)


class BulkRenamer:
    """Batch rename files with patterns."""

    def __init__(self, directory):
        self.directory = Path(directory)

    def rename(self, pattern="{n}_{original}", start=1, ext_filter=None, dry_run=False):
        """
        Rename files using a pattern.
        
        Patterns:
            {original} — Original filename (without extension)
            {ext}      — File extension
            {n}        — Sequential number
            {date}     — Current date (YYYY-MM-DD)
            {time}     — Current time (HHMMSS)
        """
        print(f"\n✏️ Bulk rename in: {self.directory}")
        print(f"   Pattern: {pattern}")
        print(f"   Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")

        files = sorted(self.directory.iterdir())
        if ext_filter:
            files = [f for f in files if f.suffix.lower() in ext_filter]

        files = [f for f in files if f.is_file()]
        count = 0

        for i, file in enumerate(files, start=start):
            new_name = pattern.format(
                original=file.stem,
                ext=file.suffix,
                n=str(i).zfill(3),
                date=datetime.now().strftime("%Y-%m-%d"),
                time=datetime.now().strftime("%H%M%S"),
            )

            if not new_name.endswith(file.suffix):
                new_name += file.suffix

            new_path = file.parent / new_name
            print(f"  {file.name} → {new_name}")

            if not dry_run:
                file.rename(new_path)
                count += 1

        print(f"\n[✓] {'Would rename' if dry_run else 'Renamed'} {count}/{len(files)} files")


def main():
    parser = argparse.ArgumentParser(
        description="AutoPilot — File & Data Automation Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python autopilot.py organize ~/Downloads
  python autopilot.py organize ~/Downloads --dry-run
  python autopilot.py duplicates ~/Pictures
  python autopilot.py clean data.csv
  python autopilot.py rename ~/Photos --pattern "vacation_{n}"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Organize
    org = subparsers.add_parser("organize", help="Organize files into category folders")
    org.add_argument("directory", help="Directory to organize")
    org.add_argument("--dry-run", action="store_true", help="Preview without moving")

    # Duplicates
    dup = subparsers.add_parser("duplicates", help="Find duplicate files")
    dup.add_argument("directory", help="Directory to scan")
    dup.add_argument("--remove", action="store_true", help="Remove duplicates (keep first)")

    # Clean
    cln = subparsers.add_parser("clean", help="Clean CSV/JSON data files")
    cln.add_argument("file", help="Data file to clean")
    cln.add_argument("--output", help="Output file path")

    # Rename
    ren = subparsers.add_parser("rename", help="Bulk rename files")
    ren.add_argument("directory", help="Directory with files to rename")
    ren.add_argument("--pattern", default="{n}_{original}", help="Rename pattern")
    ren.add_argument("--dry-run", action="store_true", help="Preview without renaming")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n💡 Interactive mode:\n")

        print("1. Organize files into folders")
        print("2. Find duplicate files")
        print("3. Clean a data file (CSV/JSON)")
        print("4. Bulk rename files")

        choice = input("\nChoose (1-4): ").strip()

        if choice == "1":
            path = input("📁 Directory path: ").strip()
            dry = input("Dry run? (y/n): ").strip().lower() == "y"
            FileOrganizer(path).organize(dry_run=dry)

        elif choice == "2":
            path = input("📁 Directory path: ").strip()
            finder = DuplicateFinder(path)
            dupes = finder.find_duplicates()
            if dupes and input("\nRemove duplicates? (y/n): ").strip().lower() == "y":
                finder.remove_duplicates(dupes)

        elif choice == "3":
            path = input("📄 File path (CSV/JSON): ").strip()
            cleaner = DataCleaner(path)
            cleaner.strip_whitespace().remove_duplicates().remove_empty().summary()
            if input("\nExport cleaned data? (y/n): ").strip().lower() == "y":
                cleaner.export()

        elif choice == "4":
            path = input("📁 Directory path: ").strip()
            pattern = input("Pattern (default: {n}_{original}): ").strip() or "{n}_{original}"
            dry = input("Dry run? (y/n): ").strip().lower() == "y"
            BulkRenamer(path).rename(pattern=pattern, dry_run=dry)

    elif args.command == "organize":
        FileOrganizer(args.directory).organize(dry_run=args.dry_run)

    elif args.command == "duplicates":
        finder = DuplicateFinder(args.directory)
        dupes = finder.find_duplicates()
        if args.remove and dupes:
            finder.remove_duplicates(dupes)

    elif args.command == "clean":
        cleaner = DataCleaner(args.file)
        cleaner.strip_whitespace().remove_duplicates().remove_empty().summary()
        cleaner.export(args.output)

    elif args.command == "rename":
        BulkRenamer(args.directory).rename(pattern=args.pattern, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
