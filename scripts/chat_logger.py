"""
Simple chat-logging persistence utility for JARVIS.
Writes per-message records to a JSONL file and can emit naive summaries.

Usage:
  from chat_logger import ChatLogger
  logger = ChatLogger()
  logger.append_message(sender='user', message='Hello')
  logger.append_message(sender='jarvis', message='Ack')
  print(logger.tail(10))
  print(logger.summarize_recent(count=10))

This is intentionally lightweight and file-based so it works offline.
"""
from __future__ import annotations
import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List


class ChatLogger:
    def __init__(self, workspace_root: Optional[str] = None,
                 recent_dir: str = 'WORK/CHAT/RECENT',
                 summaries_dir: str = 'WORK/CHAT/SUMMARIES',
                 filename: str = 'RECENT_CHAT_HISTORY.jsonl'):
        # determine workspace root
        if workspace_root:
            self.root = Path(workspace_root)
        else:
            # assume current working directory is repository root
            self.root = Path.cwd()
        self.recent_dir = self.root.joinpath(recent_dir)
        self.summaries_dir = self.root.joinpath(summaries_dir)
        self.filepath = self.recent_dir.joinpath(filename)
        os.makedirs(self.recent_dir, exist_ok=True)
        os.makedirs(self.summaries_dir, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def append_message(self, sender: str, message: str, message_id: Optional[str] = None,
                       session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        record = {
            'timestamp': self._now(),
            'sender': sender,
            'message': message,
            'message_id': message_id or str(uuid.uuid4()),
            'session_id': session_id or '',
            'metadata': metadata or {}
        }
        with open(self.filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        return record

    def tail(self, count: int = 50) -> List[Dict[str, Any]]:
        if not self.filepath.exists():
            return []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
        except Exception:
            return []
        parsed = []
        for line in lines[-count:]:
            try:
                parsed.append(json.loads(line))
            except Exception:
                continue
        return parsed

    def summarize_recent(self, count: int = 20) -> Dict[str, Any]:
        msgs = self.tail(count)
        summary = {
            'generated_at': self._now(),
            'participants': [],
            'message_count': 0,
            'summary': ''
        }
        if not msgs:
            # persist empty summary skeleton
            summary_path = self.summaries_dir.joinpath(f'summary_{datetime.now().strftime("%Y%m%dT%H%M%SZ")}.json')
            with open(summary_path, 'w', encoding='utf-8') as sf:
                json.dump(summary, sf, ensure_ascii=False, indent=2)
            return summary
        # naive summary: join messages and truncate; also list participants
        participants = sorted({m.get('sender') for m in msgs if m.get('sender')})
        joined = '\n'.join([f"[{m.get('sender')}] {m.get('message')}" for m in msgs])
        # basic heuristics: first 800 chars
        summary_text = (joined[:800] + '...') if len(joined) > 800 else joined
        summary.update({'participants': participants, 'message_count': len(msgs), 'summary': summary_text})
        # persist summary
        summary_path = self.summaries_dir.joinpath(f'summary_{datetime.now().strftime("%Y%m%dT%H%M%SZ")}.json')
        with open(summary_path, 'w', encoding='utf-8') as sf:
            json.dump(summary, sf, ensure_ascii=False, indent=2)
        return summary


if __name__ == '__main__':
    cl = ChatLogger()
    cl.append_message('user', 'Test message from user')
    cl.append_message('jarvis', 'Acknowledged, recording.')
    print('Tail:', cl.tail(5))
    print('Summary:', cl.summarize_recent(5))
