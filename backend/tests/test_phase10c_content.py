import json
import os
import sys
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from content import (  # noqa: E402
    create_content_version,
    normalize_content,
)
from main import scan_qr  # noqa: E402
from models import Base, ContentVersion, QRCode  # noqa: E402


class Phase10CContentTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.database_path = BACKEND_DIR / "test_phase10c_content.db"
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

    def make_qr(self, db, qr_id, content="https://legacy.example"):
        qr = QRCode(qr_id=qr_id, content=content, active=True, scans=0)
        db.add(qr)
        db.commit()
        db.refresh(qr)
        return qr

    def test_url_validation_accepts_http_and_https(self):
        self.assertEqual(
            normalize_content("URL", "http://example.com"),
            "http://example.com",
        )
        self.assertEqual(
            normalize_content("URL", "https://example.com/path"),
            "https://example.com/path",
        )

    def test_url_validation_rejects_unsafe_schemes_and_long_urls(self):
        for value in (
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "file:///etc/passwd",
            "ftp://example.com",
            "custom://example.com",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_content("URL", value)

        with self.assertRaises(ValueError):
            normalize_content("URL", "https://example.com/" + "a" * 2048)

    def test_text_validation(self):
        text = "Welcome\n<script>alert(1)</script>"
        self.assertEqual(normalize_content("TEXT", text), text)
        for value in ("", "   ", "\n\t"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_content("TEXT", value)
        with self.assertRaises(ValueError):
            normalize_content("TEXT", "x" * 10001)

    def valid_form(self):
        return {
            "title": "Contact request",
            "fields": [
                {
                    "name": "full_name",
                    "label": "Full name",
                    "type": "text",
                    "required": True,
                    "max_length": 100,
                },
                {
                    "name": "email",
                    "label": "Email",
                    "type": "email",
                    "required": True,
                    "max_length": 254,
                },
                {
                    "name": "message",
                    "label": "Message",
                    "type": "textarea",
                    "required": False,
                    "max_length": 2000,
                },
            ],
            "submit_label": "Send",
        }

    def test_form_validation_accepts_allowed_field_types(self):
        normalized = normalize_content("FORM", self.valid_form())
        self.assertEqual(json.loads(normalized)["fields"][2]["type"], "textarea")

    def test_form_validation_rejects_invalid_shape_and_limits(self):
        form = self.valid_form()

        for field_type in ("select", "html", "script", "file"):
            invalid = self.valid_form()
            invalid["fields"][0]["type"] = field_type
            with self.subTest(field_type=field_type):
                with self.assertRaises(ValueError):
                    normalize_content("FORM", invalid)

        too_many_fields = self.valid_form()
        too_many_fields["fields"] = too_many_fields["fields"] * 7
        with self.assertRaises(ValueError):
            normalize_content("FORM", too_many_fields)

        with self.assertRaises(ValueError):
            normalize_content("FORM", "{malformed")

        oversized = self.valid_form()
        oversized["title"] = "x" * 51000
        with self.assertRaises(ValueError):
            normalize_content("FORM", oversized)

        for field in (
            {"name": "bad name"},
            {"name": "ok", "label": "Label", "type": "text", "required": True, "max_length": 0},
            {"name": "ok", "label": "x" * 201, "type": "text", "required": True, "max_length": 1},
        ):
            invalid = self.valid_form()
            invalid["fields"][0].update(field)
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    normalize_content("FORM", invalid)

    def test_public_resolver_dispatches_url_text_and_form(self):
        db = self.session_factory()

        url_qr = self.make_qr(db, "phase10c-url")
        create_content_version(db, url_qr, "URL", "https://example.com")
        db.commit()
        url_response = scan_qr(url_qr.qr_id, db)
        self.assertEqual(url_response.status_code, 302)
        self.assertEqual(url_response.headers["location"], "https://example.com")

        text_qr = self.make_qr(db, "phase10c-text")
        text = "Hello\n<script>alert(1)</script>"
        create_content_version(db, text_qr, "TEXT", text)
        db.commit()
        text_response = scan_qr(text_qr.qr_id, db)
        self.assertEqual(text_response.status_code, 200)
        self.assertIn("text/plain", text_response.media_type)
        self.assertEqual(text_response.body.decode(), text)

        form_qr = self.make_qr(db, "phase10c-form")
        form = self.valid_form()
        form["title"] = "<script>alert(1)</script>"
        form["fields"][0]["label"] = '<img src=x onerror="alert(1)">'
        create_content_version(db, form_qr, "FORM", form)
        db.commit()
        form_response = scan_qr(form_qr.qr_id, db)
        body = form_response.body.decode()
        self.assertEqual(form_response.status_code, 200)
        self.assertIn("Content-Security-Policy", form_response.headers)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", body)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", body)
        self.assertNotIn("<script>alert(1)</script>", body)
        self.assertNotIn("<img src=x onerror=", body)
        self.assertNotIn("javascript:", body)
        self.assertNotIn("<iframe", body)
        db.close()

    def test_public_resolver_uses_legacy_url_fallback(self):
        db = self.session_factory()
        qr = self.make_qr(db, "phase10c-legacy", "https://legacy.example/path")
        response = scan_qr(qr.qr_id, db)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], "https://legacy.example/path")
        db.close()

    def test_public_resolver_rejects_unsupported_published_content_type(self):
        db = self.session_factory()
        qr = self.make_qr(db, "phase10c-unsupported")
        db.add(
            ContentVersion(
                qr=qr,
                content_type="UNKNOWN",
                content="unsupported",
                version=1,
                is_published=True,
            )
        )
        db.commit()
        with self.assertRaises(Exception) as context:
            scan_qr(qr.qr_id, db)
        self.assertIn("Unsupported", str(context.exception))
        db.close()


if __name__ == "__main__":
    unittest.main()
