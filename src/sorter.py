import os
import re
import shutil
import json
import time
import argparse
from datetime import datetime

class FileSorter:
    def __init__(self, source_dir, rules_path, log_path="sorting_log.txt"):
        self.source_dir = os.path.abspath(source_dir)
        self.rules_path = os.path.abspath(rules_path)
        self.log_path = os.path.abspath(log_path)
        self.rules = []
        self.load_rules()

    def load_rules(self):
        """Loads and compiles rules from rules.json."""
        if not os.path.exists(self.rules_path):
            # Create a default rules file if missing
            self.rules = [
                {"name": "Images", "pattern": r"\.(jpe?g|png|gif|bmp|svg)$", "destination": "organized/images"},
                {"name": "Documents", "pattern": r"\.(pdf|docx?|xlsx?|pptx?|txt)$", "destination": "organized/documents"},
                {"name": "Archives", "pattern": r"\.(zip|tar\.gz|tgz|rar|7z)$", "destination": "organized/archives"}
            ]
            os.makedirs(os.path.dirname(self.rules_path), exist_ok=True)
            with open(self.rules_path, "w", encoding="utf-8") as f:
                json.dump(self.rules, f, indent=2)
            print(f"Created default rules file at: {self.rules_path}")
        else:
            try:
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    self.rules = json.load(f)
            except Exception as e:
                print(f"Error reading rules file: {e}")
                self.rules = []

        # Compile patterns
        for rule in self.rules:
            try:
                rule["_compiled"] = re.compile(rule["pattern"], re.IGNORECASE)
            except re.error as e:
                print(f"Invalid regex pattern '{rule['pattern']}' in rule '{rule.get('name')}': {e}")
                rule["_compiled"] = None

    def log(self, message):
        """Appends log entry to sorting_log.txt."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(message)

    def get_unique_path(self, dest_path):
        """Handles naming collisions by appending '_1', '_2', etc."""
        if not os.path.exists(dest_path):
            return dest_path
        
        base, ext = os.path.splitext(dest_path)
        counter = 1
        while True:
            new_path = f"{base}_{counter}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def sort_file(self, filename):
        """Checks rules for a single file and moves it if matched."""
        file_path = os.path.join(self.source_dir, filename)
        
        # Skip directories and sorting-related files
        if os.path.isdir(file_path):
            return False
        if file_path == self.rules_path or file_path == self.log_path:
            return False

        for rule in self.rules:
            compiled = rule.get("_compiled")
            if not compiled:
                continue

            if compiled.search(filename):
                dest_dir = rule["destination"]
                # Resolve relative destination paths against source directory
                if not os.path.isabs(dest_dir):
                    dest_dir = os.path.join(self.source_dir, dest_dir)

                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, filename)
                unique_dest = self.get_unique_path(dest_path)

                try:
                    shutil.move(file_path, unique_dest)
                    self.log(f"Sorted: '{filename}' -> '{os.path.relpath(unique_dest, self.source_dir)}' (Rule: {rule['name']})")
                    return True
                except Exception as e:
                    self.log(f"Failed to move '{filename}': {e}")
                    return False
        return False

    def scan(self):
        """Performs a single-pass scan of the source directory."""
        if not os.path.exists(self.source_dir):
            print(f"Source directory '{self.source_dir}' does not exist.")
            return

        try:
            files = os.listdir(self.source_dir)
        except Exception as e:
            print(f"Error accessing source directory: {e}")
            return

        moved_count = 0
        for f in files:
            if self.sort_file(f):
                moved_count += 1
        return moved_count

    def watch(self, interval=2):
        """Starts a polling watcher loop."""
        self.log(f"Started file-sorter watcher on: {self.source_dir}")
        self.log(f"Interval: {interval} seconds. Press Ctrl+C to stop.")
        try:
            while True:
                # Reload rules dynamically if file changed (optional, but load rules again is quick)
                self.load_rules()
                self.scan()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.log("Watcher daemon stopped by user.")

def main():
    parser = argparse.ArgumentParser(description="Rules-Based Background File Sorter Daemon")
    parser.add_argument("source", help="Directory to monitor and sort files in")
    parser.add_argument("--rules", default="rules.json", help="Path to rules JSON file")
    parser.add_argument("--log", default="sorting_log.txt", help="Path to sorting history text log")
    parser.add_argument("--once", action="store_true", help="Run once instead of starting background loop")
    parser.add_argument("--interval", type=int, default=2, help="Polling interval in seconds (default: 2)")

    args = parser.parse_args()

    sorter = FileSorter(args.source, args.rules, args.log)

    if args.once:
        print(f"Scanning '{sorter.source_dir}' once...")
        count = sorter.scan()
        print(f"Scan complete. Sorted {count} file(s).")
    else:
        sorter.watch(args.interval)

if __name__ == "__main__":
    main()
