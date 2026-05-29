#!/usr/bin/env python3
"""Rapor oluşturma ve PDF export — deterministik execution katmanı"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AssistantDatabase
from pdf_generator import PDFReportGenerator

_db = AssistantDatabase()
_pdf = PDFReportGenerator()


def save_report(title: str, content: str, format_type: str = "text", file_path: str = None) -> dict:
    report_id = _db.save_report(title, content, format_type, file_path)
    return {"success": True, "report_id": report_id}


def generate_pdf(title: str, content: str) -> dict:
    try:
        path = _pdf.generate_from_text(title, content)
        return {"success": True, "file_path": path}
    except Exception as e:
        return {"success": False, "error": str(e)}


def save_and_generate(title: str, content: str, report_type: str = "Özet") -> dict:
    pdf_result = generate_pdf(title, content)
    file_path = pdf_result.get("file_path") if pdf_result["success"] else None
    db_result = save_report(title, content, "text", file_path)
    return {
        "success": db_result["success"],
        "report_id": db_result["report_id"],
        "pdf_path": file_path,
        "pdf_error": pdf_result.get("error"),
    }


def get_reports() -> list:
    return _db.get_reports()
