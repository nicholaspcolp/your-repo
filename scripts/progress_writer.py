#!/usr/bin/env python3
"""Progress writer helper for JARVIS operations.

Writes standardized per-task progress and preflight/postflight markers
to WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/ following the manifest templates.

Usage (smoke test):
  python scripts/progress_writer.py --task T-TEST --agent jarvis --rolecard rc-1 --note "started smoke test" --mode preflight
  python scripts/progress_writer.py --task T-TEST --agent jarvis --rolecard rc-1 --note "finished smoke test" --mode postflight --percent 100
"""
import argparse
import json
import os
from datetime import datetime, timezone


WORKDIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "WORK")
PROGRESS_DIR = os.path.join(WORKDIR, "JARVIS_BRAIN_OPERATIONS", "PROGRESS")

WINDOW_MANIFESTS = os.path.join(WORKDIR, "JARVIS_BRAIN_OPERATIONS", "WINDOW_MANIFESTS")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def iso_ts():
    return datetime.now(timezone.utc).isoformat()


def write_json_file(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def progress_entry(task_id, agent_id, rolecard_id, status, percent_complete=0, note=None, defection_flag=False, defection_details=None):
    return {
        "task_id": task_id,
        "owner": agent_id,
        "rolecard_id": rolecard_id,
        "status": status,
        "percent_complete": percent_complete,
        "last_updated": iso_ts(),
        "defection_flag": defection_flag,
        "defection_details": defection_details,
        "notes": note,
        "provenance": {
            "agent_id": agent_id,
            "rolecard_id": rolecard_id,
            "applied_rule": "dynamic_priority_list",
            "agent_version": None,
            "executor_id": None
        },
        "progress_summary": None,
        "docs_ref": None,
        "manifest_ref": "WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json"
    }


def write_marker(mode, task_id, agent_id, rolecard_id, note=None, percent=0, defection=False, defection_details=None):
    ensure_dir(PROGRESS_DIR)
    ensure_dir(WINDOW_MANIFESTS)
    ts = iso_ts().replace(":", "-")
    filename = f"{mode}_{task_id}_{agent_id}_{ts}.json"
    path = os.path.join(PROGRESS_DIR, filename)

    if mode == "preflight":
        obj = {
            "marker": "preflight",
            "task_id": task_id,
            "agent_id": agent_id,
            "rolecard_id": rolecard_id,
            "timestamp": iso_ts(),
            "intent_summary": note,
            "manifest_ref": "WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json"
        }
    elif mode == "postflight":
        obj = {
            "marker": "postflight",
            "task_id": task_id,
            "agent_id": agent_id,
            "rolecard_id": rolecard_id,
            "timestamp": iso_ts(),
            "outcome_summary": note,
            "defection_flag": defection,
            "defection_details": defection_details,
            "manifest_ref": "WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json",
            "user_return": {
                "status": "completed" if not defection else "blocked",
                "percent_complete": percent,
                "summary": note,
                "provenance": {
                    "agent_id": agent_id,
                    "rolecard_id": rolecard_id,
                    "agent_version": None,
                    "executor_id": None,
                    "timestamp": iso_ts()
                }
            }
        }
    elif mode == "progress":
        obj = progress_entry(task_id, agent_id, rolecard_id, "in-progress", percent, note, defection, defection_details)
    else:
        raise ValueError("mode must be 'preflight', 'postflight' or 'progress'")

    write_json_file(path, obj)
    return path


def write_window_manifest(window_id: str, task_id: str, agent_id: str, rolecard_id: str, status: str, note: str = None):
    ensure_dir(WINDOW_MANIFESTS)
    wm = {
        "window_id": window_id,
        "generated_at": iso_ts(),
        "tasks": [
            {
                "id": task_id,
                "title": f"window-snapshot {task_id}",
                "owner": agent_id,
                "status": status,
                "last_updated": iso_ts(),
                "notes": note
            }
        ],
        "notes_log": "WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/window_comm_log.csv",
        "comm_aggregate": None
    }
    path = os.path.join(WINDOW_MANIFESTS, f"{window_id}.json")
    write_json_file(path, wm)
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--rolecard", required=True)
    p.add_argument("--mode", required=True, choices=["preflight", "postflight", "progress"])
    p.add_argument("--window", required=False, help="Optional window id to emit a per-window manifest snapshot")
    p.add_argument("--note", default="")
    p.add_argument("--percent", type=int, default=0)
    p.add_argument("--defect", action="store_true")
    p.add_argument("--defect-details", default=None)
    args = p.parse_args()

    path = write_marker(args.mode, args.task, args.agent, args.rolecard, args.note, args.percent, args.defect, args.defect_details)
    print(path)

    if args.window:
        # derive a status for the window manifest snapshot
        status = "in-progress" if args.mode == "preflight" else ("completed" if args.mode == "postflight" else "in-progress")
        wm_path = write_window_manifest(args.window, args.task, args.agent, args.rolecard, status, args.note)
        print(wm_path)


if __name__ == "__main__":
    main()
