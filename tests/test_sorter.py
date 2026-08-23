import unittest
import os
import tempfile
import shutil
import json
from src.sorter import FileSorter

class TestFileSorter(unittest.TestCase):
    def setUp(self):
        # Create temp environment
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        os.makedirs(self.source_dir)

        self.rules_path = os.path.join(self.temp_dir, "rules.json")
        self.log_path = os.path.join(self.temp_dir, "sorting_log.txt")

        # Mock rules: images to "pics", code to "code_dev"
        self.mock_rules = [
            {"name": "Images", "pattern": r"\.(png|jpg)$", "destination": "pics"},
            {"name": "Code", "pattern": r"\.py$", "destination": "code_dev"}
        ]

        with open(self.rules_path, "w", encoding="utf-8") as f:
            json.dump(self.mock_rules, f)

        # Initialize Sorter
        self.sorter = FileSorter(self.source_dir, self.rules_path, self.log_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_rules(self):
        """Test rules are loaded and compiled successfully."""
        self.assertEqual(len(self.sorter.rules), 2)
        self.assertIsNotNone(self.sorter.rules[0].get("_compiled"))
        self.assertEqual(self.sorter.rules[0]["name"], "Images")

    def test_get_unique_path(self):
        """Test name collision handling."""
        file_path = os.path.join(self.temp_dir, "test.txt")
        
        # Scenario 1: Path doesn't exist
        unique_path = self.sorter.get_unique_path(file_path)
        self.assertEqual(unique_path, file_path)

        # Scenario 2: File exists, should add counter _1
        with open(file_path, "w") as f:
            f.write("hello")
            
        unique_path = self.sorter.get_unique_path(file_path)
        self.assertEqual(unique_path, os.path.join(self.temp_dir, "test_1.txt"))

    def test_sort_file(self):
        """Test that matching files are moved and ignored files are skipped."""
        # Create matching file
        img_name = "photo.png"
        img_path = os.path.join(self.source_dir, img_name)
        with open(img_path, "w") as f:
            f.write("image data")

        # Sort the file
        sorted_ok = self.sorter.sort_file(img_name)
        self.assertTrue(sorted_ok)

        # Verify it was moved
        expected_dest = os.path.join(self.source_dir, "pics", img_name)
        self.assertTrue(os.path.exists(expected_dest))
        self.assertFalse(os.path.exists(img_path))

        # Create non-matching file
        txt_name = "notes.txt"
        txt_path = os.path.join(self.source_dir, txt_name)
        with open(txt_path, "w") as f:
            f.write("text data")

        # Attempt sort
        sorted_fail = self.sorter.sort_file(txt_name)
        self.assertFalse(sorted_fail)
        self.assertTrue(os.path.exists(txt_path))

    def test_scan_full(self):
        """Test a full directory scan moves all matching files."""
        # Write files
        files = {
            "a.png": True,
            "b.py": True,
            "c.txt": False # Should not be moved
        }
        for name in files:
            with open(os.path.join(self.source_dir, name), "w") as f:
                f.write("dummy content")

        moved_count = self.sorter.scan()
        self.assertEqual(moved_count, 2)

        # Check relocations
        self.assertTrue(os.path.exists(os.path.join(self.source_dir, "pics", "a.png")))
        self.assertTrue(os.path.exists(os.path.join(self.source_dir, "code_dev", "b.py")))
        self.assertTrue(os.path.exists(os.path.join(self.source_dir, "c.txt")))

if __name__ == "__main__":
    unittest.main()
