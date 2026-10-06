import os
import sys
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from content import (  # noqa: E402
    backfill_legacy_url_content,
    create_url_content_version,
    get_current_content,
)
from models import Base, QRCode  # noqa: E402


class ContentVersionTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.database_path = BACKEND_DIR / "test_content_versions.db"
        if cls.database_path.exists():
            os.remove(cls.database_path)

        cls.engine = create_engine(
            f"sqlite:///{cls.database_path}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(cls.engine)
        cls.session_factory = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()
        if cls.database_path.exists():
            os.remove(cls.database_path)

    def test_legacy_qr_is_backfilled_as_url_content(self):
        db = self.session_factory()
        qr = QRCode(qr_id="legacy-qr", content="https://example.com")
        db.add(qr)
        db.commit()

        self.assertEqual(backfill_legacy_url_content(db), 1)
        db.refresh(qr)
        self.assertEqual(get_current_content(qr), "https://example.com")
        self.assertEqual(len(qr.content_versions), 1)
        self.assertEqual(qr.content_versions[0].content_type, "URL")
        db.close()

    def test_url_update_publishes_new_version_and_keeps_legacy_content(self):
        db = self.session_factory()
        qr = QRCode(qr_id="versioned-qr", content="https://example.com")
        db.add(qr)
        db.commit()
        backfill_legacy_url_content(db)
        db.refresh(qr)

        create_url_content_version(db, qr, "https://example.org")
        qr.content = "https://example.org"
        db.commit()
        db.refresh(qr)

        self.assertEqual(get_current_content(qr), "https://example.org")
        self.assertEqual(qr.content, "https://example.org")
        self.assertEqual(
            [version.version for version in qr.content_versions],
            [1, 2],
        )
        self.assertEqual(
            [version.is_published for version in qr.content_versions],
            [False, True],
        )
        db.close()


if __name__ == "__main__":
    unittest.main()
