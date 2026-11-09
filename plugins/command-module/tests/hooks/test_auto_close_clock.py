"""Regression tests for report-only checks and compatible manual clocks.
Run: python3 -m unittest discover -s plugins/command-module/tests/hooks -p test_auto_close_clock.py
"""
import csv
import hashlib
import importlib.util
import json
import os
import plistlib
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

PLUGIN = Path(__file__).resolve().parents[2]
CHECK = PLUGIN / "staging/hooks/clock-check.py"
SHIM = PLUGIN / "staging/hooks/auto-close-clock.py"
CI = PLUGIN / "scripts/clock-in.py"
INSTALL = PLUGIN / "scripts/install-auto-close-launchagent.sh"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

checker = load("clock_check_tested", CHECK)
ci = load("clock_in_tested", CI)


class ClockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.clocks = self.root / "tracking/.active-clocks"
        self.clocks.mkdir(parents=True)
        (self.root / "reports").mkdir()
        (self.root / "reports/timesheet.csv").write_text("date,start,end\n2026-11-08,19:10,21:02\n")
        (self.root / "tracking/history.jsonl").write_text('{"existing":true}\n')

    def put(self, name, data):
        p = self.clocks / (name + ".json")
        p.write_text(json.dumps(data))
        return p

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def base(self):
        return {"session_id": "session-a", "repo": "resources",
                "opened_at": "2026-11-09T19:00:00", "start": "2026-11-09T19:00:00",
                "last_activity": "2026-11-09T21:00:00"}

    def test_preserves_every_clock_and_time_record_repeatedly(self):
        self.put("active-after-20", self.base())
        self.put("legacy", {"start": "2026-11-08T19:10:43+01:00"})
        self.put("armed", {"opened_at": "2026-11-09T19:00:00", "start": None})
        self.put("wrapped", {"opened_at": "2026-11-08T19:00:00", "start": None, "wrapped_at": "2026-11-09T19:00:00"})
        self.put("stale", {**self.base(), "start": "2026-11-08T19:00:00", "last_activity": "2026-11-08T21:00:00"})
        (self.clocks / "malformed.json").write_text("{bad json")
        before = self.snapshot()
        for _ in range(2):
            report = checker.build_report(self.root, datetime(2026, 11, 9, 21, 5))
            self.assertEqual(len(report["clocks"]), 6)
            self.assertGreaterEqual(report["review_count"], 3)
            self.assertEqual(before, self.snapshot())

    def test_invalid_order_future_and_accrual_require_review(self):
        now = datetime(2026, 11, 9, 21, 5)
        cases = [
            {**self.base(), "last_activity": "2026-11-09T18:59:00"},
            {"opened_at": "2026-11-10T19:00:00", "start": None},
            {"opened_at": "2026-11-09T19:00:00", "start": None, "accrued_seconds": 600},
            {**self.base(), "accrued_seconds": -1},
        ]
        for index, clock in enumerate(cases):
            self.put("invalid-" + str(index), clock)
        report = checker.build_report(self.root, now)
        self.assertEqual(report["review_count"], len(cases))

    def test_report_creation_only_adds_report_files(self):
        self.put("running", self.base())
        before = self.snapshot()
        self.assertEqual(checker.main(["--mission-control", str(self.root)]), 0)
        after = self.snapshot()
        for path, data in before.items():
            self.assertEqual(data, after[path])
        self.assertEqual(set(after)-set(before),
                         {"reports/clock-check/latest.json", "reports/clock-check/latest.md"})

    def test_legacy_entrypoint_is_report_only(self):
        self.put("legacy", {"start": "2026-11-08T19:10:00"})
        before = self.snapshot()
        result = subprocess.run([sys.executable, str(SHIM), "--mission-control", str(self.root), "--stdout-only"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["clock_count"], 1)
        self.assertEqual(self.snapshot(), before)

    def test_missing_directory_and_invalid_siblings(self):
        missing = checker.build_report(self.root / "absent")
        self.assertEqual(missing["clocks"], [])
        self.put("not-object", [])
        self.put("invalid-time", {"start": "not-a-date"})
        report = checker.build_report(self.root)
        self.assertEqual(report["review_count"], 2)

    def test_unreadable_directory_reports_failure_not_clean_empty(self):
        with patch.object(Path, "iterdir", side_effect=PermissionError("denied clock directory")):
            report = checker.build_report(self.root)
        self.assertTrue(report["errors"])
        self.assertIn("denied clock directory", report["errors"][0])

    def test_read_failure_and_disappearing_file_are_preserved_as_review(self):
        p = self.clocks / "gone.json"
        row = checker.inspect_clock(p, datetime.now())
        self.assertTrue(row["needs_review"])
        self.assertFalse(p.exists())
        p.write_text("{}")
        with patch.object(Path, "read_text", side_effect=PermissionError("unreadable")):
            row = checker.inspect_clock(p, datetime.now())
        self.assertIn("unreadable", row["reasons"][0])
        self.assertTrue(p.exists())

    def test_symlink_clock_not_followed(self):
        target = self.root / "private"
        target.write_text("private")
        (self.clocks / "linked.json").symlink_to(target)
        report = checker.build_report(self.root)
        self.assertTrue(report["clocks"][0]["needs_review"])
        self.assertEqual(target.read_text(), "private")

    def test_new_manual_clock_full_schema(self):
        now = datetime(2026, 11, 9, 6, 51, 32)
        data = ci.new_clock("my-session", "/some/repo", {"repo":"resources","source":"tasks-touched"}, now)
        for key in ["start","opened_at","work_start","last_activity"]:
            self.assertEqual(data[key], "2026-11-09T06:51:32")
        for key in ["accrued_seconds","tool_count","turn_count"]:
            self.assertEqual(data[key], 0)
        self.assertIsNone(data["wrapped_at"])
        self.assertIsNone(data["wrap_armed_at"])
        self.assertEqual(data["source_at_start"], "manual-ci")

    def test_existing_and_concurrent_clocks_are_not_overwritten(self):
        data = ci.new_clock("my-session", "/some/repo", {"repo":"resources"})
        results=[]
        threads=[threading.Thread(target=lambda: results.append(ci.create_clock(self.clocks,data))) for _ in range(8)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(sum(created for created, _ in results),1)
        before=(self.clocks/"my-session.json").read_bytes()
        created, saved = ci.create_clock(self.clocks,{**data,"start":"changed"})
        self.assertFalse(created)
        self.assertEqual(saved,data)
        self.assertEqual((self.clocks/"my-session.json").read_bytes(),before)
        self.assertEqual(list(self.clocks.glob("*.tmp")),[])

    def test_malformed_existing_clock_is_not_repaired(self):
        p=self.clocks/"my-session.json"
        p.write_text("bad")
        with self.assertRaises(ValueError):
            ci.create_clock(self.clocks,ci.new_clock("my-session","/",{}))
        self.assertEqual(p.read_text(),"bad")

    def test_invalid_session_ids_refused(self):
        for sid in ["", "../other", "/absolute", "spaces not allowed", ".hidden"]:
            with self.assertRaises(ValueError):
                ci.new_clock(sid,"/",{})

    @unittest.skipUnless(hasattr(time,"tzset"), "Requires Unix timezone test control")
    def test_offsets_z_midnight_and_dst_convert_to_local(self):
        old=os.environ.get("TZ")
        os.environ["TZ"]="Europe/Amsterdam"
        time.tzset()
        try:
            self.assertEqual(checker.local_time("2026-11-09T06:00:00+01:00"),datetime(2026,11,9,6))
            self.assertEqual(checker.local_time("2026-11-09T05:00:00Z"),datetime(2026,11,9,6))
            self.assertEqual(checker.local_time("2026-07-09T05:00:00+02:00"),datetime(2026,7,9,5))
            self.assertEqual(checker.local_time("2026-11-08T23:30:00Z"),datetime(2026,11,9,0,30))
            d=ci.new_clock("dst","/",{},datetime(2026,10,25,1,30,tzinfo=timezone.utc))
            self.assertEqual(d["start"],"2026-10-25T02:30:00")
        finally:
            if old is None: os.environ.pop("TZ",None)
            else: os.environ["TZ"]=old
            time.tzset()


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.home=self.root/"home"
        self.bin=self.root/"bin"
        self.bin.mkdir()
        self.home.mkdir()
        self.log=self.root/"launch.log"
        mock=self.bin/"launchctl"
        mock.write_text("""#!/bin/sh
printf '%s\\n' "$*" >> "$LAUNCH_LOG"
if [ "$1" = print ]; then exit 1; fi
exit 0
""")
        mock.chmod(0o755)
        self.env={**os.environ,"HOME":str(self.home),"PATH":str(self.bin)+":"+os.environ["PATH"],"LAUNCH_LOG":str(self.log)}
    def run_install(self,*extra):
        return subprocess.run(["/bin/bash",str(INSTALL),*extra],env=self.env,capture_output=True,text=True)
    def test_installer_retires_closure_and_is_repeatably_report_only(self):
        for _ in range(2):
            r=self.run_install("--no-cron-prompt")
            self.assertEqual(r.returncode,0,r.stderr)
        args=self.log.read_text()
        self.assertIn("disable gui/",args)
        self.assertIn("/com.esther.auto-close-clock",args)
        self.assertNotIn("enable gui/"+str(os.getuid())+"/com.esther.auto-close-clock",args)
        self.assertNotIn("kickstart",args)
        plistdir=self.home/"Library/LaunchAgents"
        for label in ["com.esther.clock-check","com.esther.auto-close-clock"]:
            p=plistlib.loads((plistdir/(label+".plist")).read_bytes())
            self.assertTrue(p["ProgramArguments"][1].endswith("/clock-check.py"))
        for host in [".claude",".codex"]:
            shim=(self.home/host/"hooks/auto-close-clock.py").read_text()
            self.assertIn("runpy",shim)
            self.assertNotIn("unlink",shim)
    def test_disabled_report_job_is_enabled_before_bootstrap(self):
        r = self.run_install()
        self.assertEqual(r.returncode, 0, r.stderr)
        calls = self.log.read_text().splitlines()
        enable = next(i for i, v in enumerate(calls) if v.startswith("enable ") and v.endswith("/com.esther.clock-check"))
        bootstrap = next(i for i, v in enumerate(calls) if v.startswith("bootstrap "))
        self.assertLess(enable, bootstrap)

    def test_old_override_refused_before_any_state_change(self):
        source=self.root/"old"
        source.mkdir()
        (source/"auto-close-clock.py").write_text("delete everything")
        r=self.run_install("--hook-source",str(source))
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(self.log.exists())
        self.assertEqual(list(self.home.iterdir()),[])
    def test_safe_override_never_copies_its_destructive_compatibility_script(self):
        source=self.root/"override"
        source.mkdir()
        (source/"clock-check.py").write_bytes(CHECK.read_bytes())
        (source/"auto-close-clock.py").write_text("delete everything")
        r=self.run_install("--hook-source",str(source))
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertNotIn("delete everything",(self.home/".claude/hooks/auto-close-clock.py").read_text())


if __name__ == "__main__":
    unittest.main()
