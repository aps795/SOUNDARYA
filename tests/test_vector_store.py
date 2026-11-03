"""Unit tests for Local Semantic Vector Store and Document Search."""

import unittest
import tempfile
import shutil
from pathlib import Path
from app.memory.vector_store import LocalVectorStore


class TestVectorStore(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.store = LocalVectorStore(storage_dir=Path(self.test_dir))

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_vector_store_ingestion_and_search(self) -> None:
        sample_doc = Path(self.test_dir) / "soundarya_architecture.txt"
        sample_doc.write_text(
            "SOUNDARYA incorporates a modular AI operating engine.\n\n"
            "The personal database uses SQLite and SQLAlchemy for encrypted memory.\n\n"
            "Voice synthesis is supported natively through Piper TTS and macOS speech engines."
        )

        count = self.store.ingest_document(sample_doc)
        self.assertEqual(count, 3)

        # Query matching 2nd chunk
        results = self.store.search("database SQLite SQLAlchemy")
        self.assertGreater(len(results), 0)
        self.assertIn("SQLite", results[0]["content"])
        self.assertEqual(results[0]["filename"], "soundarya_architecture.txt")

        # Query matching 3rd chunk
        results_voice = self.store.search("voice synthesis audio")
        self.assertGreater(len(results_voice), 0)
        self.assertIn("Piper TTS", results_voice[0]["content"])


if __name__ == "__main__":
    unittest.main()
