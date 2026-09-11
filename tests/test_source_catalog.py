import unittest
from pathlib import Path

from src.knowledge.source_catalog.faq_canonical import parse_faq_md
from src.knowledge.source_catalog.questions import fingerprint, normalize_question
from src.knowledge.source_catalog.scanner import FileFact, ScanRaw, classify_rel, discover_features, parse_go_file
from src.knowledge.source_catalog.schema import FeatureRecord


class SourceCatalogTests(unittest.TestCase):
    def test_normalize_similar_domain_questions(self):
        a = normalize_question("چطور دامنه اضافه کنم؟")
        b = normalize_question("روش اضافه کردن Domain چیه؟")
        self.assertIn("domain", a)
        self.assertIn("domain", b)
        self.assertEqual(fingerprint("How do I add a domain?"), fingerprint("how do i add a domain"))

    def test_classify_skips_vendor(self):
        self.assertEqual(classify_rel("vendor/fyne/x.go"), "skip")
        self.assertEqual(classify_rel("internal/ui/app.go"), "ui")

    def test_parse_opid(self):
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "opstate.go"
            p.write_text('package config\n\tOpFullDeploy OpID = "full_deploy"\n', encoding="utf-8")
            fact = parse_go_file(p, "internal/config/opstate.go")
            self.assertIn("full_deploy", fact.op_ids)

    def test_discover_includes_legacy_and_leftover(self):
        raw = ScanRaw(
            root="x",
            files=[
                FileFact(rel="internal/config/opstate.go", kind="internal", op_ids=["deploy_chain", "full_deploy"], sha256="a"),
                FileFact(rel="internal/ui/splash.go", kind="ui", symbols=["showSplash"], sha256="b"),
                FileFact(rel="internal/ui/mystery.go", kind="ui", symbols=["buildMystery"], sha256="c"),
            ],
            file_index_hash="abc",
            scanned_at="t",
            go_files=3,
            ui_prod_files=2,
            packages=["ui", "config"],
        )
        feats = discover_features(raw)
        ids = {f.id for f in feats}
        self.assertIn("deploy_chain_legacy", ids)
        self.assertIn("first_run_splash", ids)
        self.assertTrue(any(f.id.startswith("src_internal_ui_mystery") for f in feats))
        legacy = next(f for f in feats if f.id == "deploy_chain_legacy")
        self.assertEqual(legacy.status, "deprecated")

    def test_faq_parse_ids(self):
        md = "### Q001 Hello?\nAns 1\n\n### Q002 Next\nAns 2\n"
        items = parse_faq_md(md)
        self.assertEqual([i["id"] for i in items], ["Q001", "Q002"])

    def test_feature_record_roundtrip(self):
        rec = FeatureRecord(id="x", name="X", category="SSH")
        self.assertEqual(FeatureRecord.from_dict(rec.to_dict()).id, "x")


if __name__ == "__main__":
    unittest.main()
