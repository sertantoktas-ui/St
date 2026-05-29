#!/usr/bin/env python3
"""Not ve arama geçmişi işlemleri — deterministik execution katmanı"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AssistantDatabase

_db = AssistantDatabase()


def add_note(content: str) -> dict:
    if not content.strip():
        return {"success": False, "error": "Not içeriği boş olamaz"}
    note_id = _db.add_note(content)
    return {"success": True, "note_id": note_id}


def list_notes() -> list:
    return _db.get_notes()


def search_notes(query: str) -> list:
    return _db.search_notes(query)


def delete_note(note_id: int) -> dict:
    success = _db.delete_note(note_id)
    return {"success": success, "note_id": note_id}


def save_search(query: str, results: str) -> dict:
    search_id = _db.save_search(query, results)
    return {"success": True, "search_id": search_id}


def get_search_history(limit: int = 10) -> list:
    return _db.get_search_history(limit)
