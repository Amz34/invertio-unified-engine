#!/usr/bin/env python3
"""agy_transcript_compactor.py: Enterprise Autonomous Transcript Compaction & Context Quota Defense.

Eliminates O(N^2) context explosion by safely archiving and compacting bloated conversation
transcripts (>40 steps) while strictly preserving:
1. Lossless full gzip archives in /home/ubuntu/ops/antigravity/archive_transcripts/<cid>/
2. Initial user intent and prompt metadata (Step 0)
3. Semantic Memory Graph (decisions locked, files touched, mission objectives) injected into Turn 1
4. Tail execution context (last 15 steps) for seamless session resumption
5. Exclusion of currently active or recently touched conversations (<30 min)
"""

from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone

ARCHIVE_DIR = "/home/ubuntu/ops/antigravity/archive_transcripts"
LOG_FILE = "/home/ubuntu/ops/logs/agy_transcript_compactor.log"

RUNTIMES = [
    ("/home/ubuntu/.gemini/antigravity-cli", "primary_aamir"),
    ("/home/ubuntu/agy-argon-home/.gemini/antigravity-cli", "secondary_amer"),
]


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def extract_semantic_signals(lines: list[str]) -> dict:
    """Extracts locked decisions, modified files, and goals from pruned historical turns."""
    decisions = []
    files_touched = set()
    errors_seen = []
    user_intents = []
    
    file_pattern = re.compile(r"(/[a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9]+)")
    decision_pattern = re.compile(
        r"(?:Decided|Architectural choice|Root cause|Solution|Configured|Fixed|Implemented):\s*([^\n\.]+)",
        re.IGNORECASE
    )
    
    for l in lines:
        try:
            d = json.loads(l)
            src = d.get("source", "")
            c = str(d.get("content", ""))
            
            if src == "USER" and len(c.strip()) > 10:
                clean_u = re.sub(r"<[^>]+>", "", c).strip()
                if clean_u:
                    user_intents.append(clean_u[:160])
            
            for m in decision_pattern.finditer(c):
                dec = m.group(1).strip()
                if len(dec) > 5 and len(dec) < 140:
                    decisions.append(dec)
                
            for f in file_pattern.findall(c):
                if any(f.endswith(ext) for ext in [".py", ".sh", ".json", ".md", ".yaml", ".yml", ".ts", ".js", ".png"]):
                    if not f.startswith("/proc") and not f.startswith("/sys") and not f.startswith("/dev"):
                        files_touched.add(f)
                        
            if any(term in c.lower() for term in ["traceback", "exception", "syntaxerror", "failed with code"]):
                if len(c) < 220:
                    errors_seen.append(c.strip())
        except Exception:
            pass
            
    return {
        "user_intents": list(dict.fromkeys(user_intents))[:3],
        "decisions": list(dict.fromkeys(decisions))[:8],
        "files_touched": sorted(list(files_touched))[:12],
        "recent_alerts": errors_seen[-3:]
    }


def is_active_or_recent(path: str, age_limit_sec: int = 1800, current_cid: str | None = None) -> bool:
    try:
        if current_cid and current_cid in path:
            return True
        mtime = os.path.getmtime(path)
        if (time.time() - mtime) < age_limit_sec:
            return True
    except Exception:
        return True
    return False


def compact_file(path: str, live: bool = False, max_steps: int = 40, keep_tail: int = 15) -> dict | None:
    try:
        parts = path.split("/")
        cid = parts[-4] if "brain" in parts else os.path.basename(os.path.dirname(os.path.dirname(path)))
        session_dir = os.path.dirname(os.path.dirname(os.path.dirname(path)))
        
        with open(path, "r", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if len(lines) <= max_steps:
            return None
        
        # Calculate tokens before
        total_tok_before = 0
        for line in lines:
            try:
                d = json.loads(line)
                total_tok_before += (
                    d.get("input_tokens", 0) + d.get("cache_read_tokens", 0) + d.get("output_tokens", 0)
                )
            except Exception:
                pass
        
        step_0 = lines[0]
        tail_start_idx = max(1, len(lines) - keep_tail)
        pruned_lines = lines[1:tail_start_idx]
        tail_lines = lines[tail_start_idx:]
        
        # Extract Semantic Memory State from pruned history
        semantic = extract_semantic_signals(pruned_lines)
        manifest_data = {
            "conversation_id": cid,
            "compacted_at": datetime.now(timezone.utc).isoformat(),
            "original_steps": len(lines),
            "retained_tail_steps": len(tail_lines),
            "archive_path": f"{ARCHIVE_DIR}/{cid}/transcript.jsonl.gz",
            "semantic_state": semantic
        }
        
        # Construct human-readable Semantic State Manifest block for turn 1
        lines_manifest = [
            f"[SEMANTIC STATE MANIFEST - COMPACTED CONTEXT DEFENSE]",
            f"• Prior Steps Compacted: {len(pruned_lines)} turns archived to cold vault.",
            f"• Full Lossless Archive: {ARCHIVE_DIR}/{cid}/transcript.jsonl.gz"
        ]
        if semantic["user_intents"]:
            lines_manifest.append("• Captured Mission Objectives:")
            for obj in semantic["user_intents"]:
                lines_manifest.append(f"  - {obj}")
        if semantic["decisions"]:
            lines_manifest.append("• Key Decisions & Architecture Locked:")
            for dec in semantic["decisions"]:
                lines_manifest.append(f"  - {dec}")
        if semantic["files_touched"]:
            lines_manifest.append("• Critical Active Files:")
            for ft in semantic["files_touched"][:8]:
                lines_manifest.append(f"  - {ft}")
                
        manifest_text = "\n".join(lines_manifest)
        
        checkpoint = json.dumps({
            "step_index": 1,
            "source": "SYSTEM",
            "type": "SYSTEM_MESSAGE",
            "status": "DONE",
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "content": manifest_text
        })
        
        compacted_lines = [step_0, checkpoint]
        # Re-index tail steps cleanly
        curr_idx = 2
        for t_line in tail_lines:
            try:
                td = json.loads(t_line)
                td["step_index"] = curr_idx
                compacted_lines.append(json.dumps(td))
                curr_idx += 1
            except Exception:
                compacted_lines.append(t_line)
                curr_idx += 1
        
        # Calculate tokens after
        total_tok_after = 0
        for line in compacted_lines:
            try:
                d = json.loads(line)
                total_tok_after += (
                    d.get("input_tokens", 0) + d.get("cache_read_tokens", 0) + d.get("output_tokens", 0)
                )
            except Exception:
                pass
        
        res = {
            "cid": cid,
            "path": path,
            "original_lines": len(lines),
            "compacted_lines": len(compacted_lines),
            "pruned_steps": len(pruned_lines),
            "decisions_preserved": len(semantic["decisions"]),
            "files_indexed": len(semantic["files_touched"]),
            "tokens_before": total_tok_before,
            "tokens_after": total_tok_after,
            "tokens_saved": max(0, total_tok_before - total_tok_after),
        }
        
        if live:
            # 1. Lossless backup to archive
            dest_dir = os.path.join(ARCHIVE_DIR, cid)
            os.makedirs(dest_dir, exist_ok=True)
            archive_target = os.path.join(dest_dir, "transcript.jsonl.gz")
            
            with gzip.open(archive_target, "wt", encoding="utf-8") as gz_out:
                for l in lines:
                    gz_out.write(l + "\n")
            
            # Verify backup
            if not os.path.isfile(archive_target) or os.path.getsize(archive_target) == 0:
                raise RuntimeError(f"Backup verification failed for {archive_target}")
                
            # 2. Persist session semantic manifest
            manifest_file = os.path.join(session_dir, "semantic_state_manifest.json")
            try:
                with open(manifest_file, "w", encoding="utf-8") as mf:
                    json.dump(manifest_data, mf, indent=2)
            except Exception:
                pass
            
            # 3. Atomic write to live path
            tmp_target = path + ".compaction_tmp"
            with open(tmp_target, "w", encoding="utf-8") as f_out:
                for l in compacted_lines:
                    f_out.write(l + "\n")
            
            os.replace(tmp_target, path)
            res["status"] = "compacted_and_archived"
        else:
            res["status"] = "dry_run_candidate"
            
        return res
    except Exception as e:
        log(f"[ERROR] Failed to compact {path}: {e}")
        return None


def run_compactor(live: bool = False, max_steps: int = 40, keep_tail: int = 15, current_cid: str | None = None) -> dict:
    log(f"Starting transcript compactor (live={live}, max_steps={max_steps}, keep_tail={keep_tail})")
    total_scanned = 0
    compacted_count = 0
    total_tokens_saved = 0
    candidates = []
    
    for base_dir, label in RUNTIMES:
        pattern = os.path.join(base_dir, "brain/*/.system_generated/logs/transcript.jsonl")
        files = glob.glob(pattern)
        total_scanned += len(files)
        
        for p in files:
            if is_active_or_recent(p, age_limit_sec=1800, current_cid=current_cid):
                continue
            
            c_res = compact_file(p, live=live, max_steps=max_steps, keep_tail=keep_tail)
            if c_res:
                candidates.append(c_res)
                compacted_count += 1
                total_tokens_saved += c_res["tokens_saved"]
    
    summary = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "live": live,
        "scanned": total_scanned,
        "compacted": compacted_count,
        "tokens_saved": total_tokens_saved,
    }
    
    log(
        f"Compaction completed: scanned {total_scanned} transcripts, "
        f"compacted {compacted_count} sessions, "
        f"total cumulative tokens prevented: {total_tokens_saved:,}"
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description="AGY Transcript Compactor with Semantic Memory Graph")
    parser.add_argument("--live", action="store_true", help="Execute real live compaction and archival")
    parser.add_argument("--max-steps", type=int, default=40, help="Max step threshold before compaction")
    parser.add_argument("--keep-tail", type=int, default=15, help="Number of tail steps to preserve")
    parser.add_argument("--current-cid", type=str, default=None, help="Current active conversation ID to exclude")
    args = parser.parse_args()
    
    curr_cid = args.current_cid or os.environ.get("CONVERSATION_ID")
    res = run_compactor(live=args.live, max_steps=args.max_steps, keep_tail=args.keep_tail, current_cid=curr_cid)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
