"""
Session grades database. Stores per-session scores and raw metrics.

Usage:
    from tools.grades_db import GradesDB

    db = GradesDB()  # creates grades.db in casestudies/
    db.record(
        session_id="9ede6cc5",
        date="2026-03-22",
        website="todomvc.com",
        gate_pass=True,
        d1_quality=16, d2_turns=0, d3_tokens=5, d4_time=0, d5_process=3, d6_docs=7,
        raw_metrics={...}
    )
    db.show_all()
"""

import json
import os
import sqlite3


DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "grades.db"
)


class GradesDB:
    def __init__(self, path=None):
        self.path = path or DB_PATH
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                website TEXT NOT NULL,
                gate_pass INTEGER NOT NULL,
                d1_quality INTEGER NOT NULL,
                d2_turns INTEGER NOT NULL,
                d3_tokens INTEGER NOT NULL,
                d4_time INTEGER NOT NULL,
                d5_process INTEGER NOT NULL,
                d6_docs INTEGER NOT NULL,
                total INTEGER NOT NULL,
                grade TEXT NOT NULL,
                duration_min REAL,
                total_turns INTEGER,
                text_only_pct REAL,
                output_tokens INTEGER,
                wasted_calls INTEGER,
                tool_errors INTEGER,
                notes TEXT,
                raw_metrics TEXT
            )
        """)
        self.conn.commit()

    def record(self, session_id, date, website, gate_pass,
               d1_quality, d2_turns, d3_tokens, d4_time, d5_process, d6_docs,
               raw_metrics=None, notes=""):
        total = d1_quality + d2_turns + d3_tokens + d4_time + d5_process + d6_docs
        if not gate_pass:
            grade = "D"
        elif total >= 85:
            grade = "A"
        elif total >= 70:
            grade = "B"
        elif total >= 55:
            grade = "C"
        else:
            grade = "D"

        metrics = raw_metrics or {}
        self.conn.execute("""
            INSERT OR REPLACE INTO sessions VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            session_id, date, website, int(gate_pass),
            d1_quality, d2_turns, d3_tokens, d4_time, d5_process, d6_docs,
            total, grade,
            metrics.get("duration_min"),
            metrics.get("total_turns"),
            metrics.get("text_only_pct"),
            metrics.get("output_tokens"),
            metrics.get("wasted_tool_calls"),
            metrics.get("tool_errors"),
            notes,
            json.dumps(metrics, default=str),
        ))
        self.conn.commit()
        return total, grade

    def show_all(self):
        rows = self.conn.execute(
            "SELECT * FROM sessions ORDER BY date"
        ).fetchall()
        if not rows:
            print("No sessions recorded.")
            return

        header = f"{'Date':12s} {'Website':20s} {'Gate':4s} {'D1':3s} {'D2':3s} {'D3':3s} {'D4':3s} {'D5':3s} {'D6':3s} {'Tot':4s} {'Grd':3s} {'Turns':5s} {'Tokens':7s}"
        print(header)
        print("-" * len(header))
        for r in rows:
            print(
                f"{r['date']:12s} {r['website']:20s} "
                f"{'P' if r['gate_pass'] else 'F':4s} "
                f"{r['d1_quality']:3d} {r['d2_turns']:3d} {r['d3_tokens']:3d} "
                f"{r['d4_time']:3d} {r['d5_process']:3d} {r['d6_docs']:3d} "
                f"{r['total']:4d} {r['grade']:3s} "
                f"{r['total_turns'] or '?':>5} {r['output_tokens'] or '?':>7}"
            )

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = GradesDB()

    # Record session 001
    db.record(
        session_id="9ede6cc5",
        date="2026-03-22",
        website="todomvc.com",
        gate_pass=True,
        d1_quality=16,
        d2_turns=0,
        d3_tokens=5,
        d4_time=0,
        d5_process=3,
        d6_docs=7,
        raw_metrics={
            "duration_min": 24.9,
            "total_turns": 109,
            "text_only_pct": 47.7,
            "output_tokens": 37600,
            "wasted_tool_calls": 9,
            "tool_errors": 7,
        },
        notes="First session. No tooling, no process. 8 min wasted on wrong tools.",
    )

    db.show_all()
    db.close()
