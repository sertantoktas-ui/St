#!/usr/bin/env python3
"""Görev CRUD işlemleri — deterministik execution katmanı"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AssistantDatabase

_db = AssistantDatabase()


def add_task(title: str, description: str = "", priority: str = "medium") -> dict:
    task_id = _db.add_task(title, description, priority)
    return {"success": True, "task_id": task_id, "title": title, "priority": priority}


def get_tasks(status: str = "pending") -> list:
    return _db.get_tasks(status)


def complete_task(task_id: int) -> dict:
    success = _db.complete_task(task_id)
    return {"success": success, "task_id": task_id}


def delete_task(task_id: int) -> dict:
    success = _db.delete_task(task_id)
    return {"success": success, "task_id": task_id}


def get_statistics() -> dict:
    return _db.get_statistics()
