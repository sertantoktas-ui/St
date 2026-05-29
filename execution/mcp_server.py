#!/usr/bin/env python3
"""
Kişisel Asistan — MCP Server (stdio)

Başlatma:
  python execution/mcp_server.py

Claude Code ile kullanım (.mcp.json):
  {
    "mcpServers": {
      "kisisel-asistan": {
        "command": "python",
        "args": ["execution/mcp_server.py"],
        "cwd": "<repo-yolu>"
      }
    }
  }
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from execution.tool_executor import execute

mcp = FastMCP("kisisel-asistan")


@mcp.tool()
def add_task(title: str, description: str = "", priority: str = "medium") -> str:
    """Yeni görev ekle."""
    return execute("add_task", {"title": title, "description": description, "priority": priority})


@mcp.tool()
def list_tasks(status: str = "pending") -> str:
    """Görevleri listele. status: pending | completed"""
    return execute("list_tasks", {"status": status})


@mcp.tool()
def complete_task(task_id: int) -> str:
    """Görevi tamamlandı olarak işaretle."""
    return execute("complete_task", {"task_id": task_id})


@mcp.tool()
def save_email(recipient: str, subject: str, body: str, tone: str = "formal", send_now: bool = False) -> str:
    """Email taslağı oluştur ve kaydet. send_now=True ise SMTP ile gönder."""
    return execute("save_email", {
        "recipient": recipient, "subject": subject,
        "body": body, "tone": tone, "send_now": send_now,
    })


@mcp.tool()
def create_report(title: str, content: str) -> str:
    """Rapor oluştur ve PDF olarak kaydet."""
    return execute("create_report", {"title": title, "content": content})


@mcp.tool()
def add_note(content: str) -> str:
    """Not ekle."""
    return execute("add_note", {"content": content})


@mcp.tool()
def list_notes(search: str = "") -> str:
    """Notları listele. search parametresiyle filtrele."""
    return execute("list_notes", {"search": search})


@mcp.tool()
def get_statistics() -> str:
    """Asistan istatistiklerini göster."""
    return execute("get_statistics", {})


@mcp.tool()
def notebooklm_add_source(source: str, source_type: str = "url", title: str = "", notebook_id: str = "") -> str:
    """NotebookLM not defterine URL veya metin kaynağı ekle. source_type: url | text"""
    return execute("notebooklm_add_source", {
        "source": source,
        "source_type": source_type,
        "title": title,
        "notebook_id": notebook_id or None,
    })


@mcp.tool()
def notebooklm_query(question: str, notebook_id: str = "") -> str:
    """NotebookLM not defterine soru sor."""
    return execute("notebooklm_query", {"question": question, "notebook_id": notebook_id or None})


@mcp.tool()
def notebooklm_list() -> str:
    """NotebookLM'deki tüm not defterlerini listele."""
    return execute("notebooklm_list", {})


if __name__ == "__main__":
    mcp.run(transport="stdio")
