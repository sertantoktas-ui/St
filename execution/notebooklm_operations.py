#!/usr/bin/env python3
"""
NotebookLM işlemleri — deterministik execution katmanı.
notebooklm-mcp-server üzerinden çalışır (npx notebooklm-mcp-server auth ile auth gerekli).
"""

import sys
import os
import json
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

NOTEBOOK_ID = os.getenv("NOTEBOOKLM_NOTEBOOK_ID", "4aa95fc5-5f77-4575-afc6-4b9e6766da6f")
NOTEBOOK_URL = os.getenv(
    "NOTEBOOKLM_NOTEBOOK_URL",
    f"https://notebooklm.google.com/notebook/{NOTEBOOK_ID}",
)


def _mcp_call(tool: str, args: dict) -> dict:
    """notebooklm-mcp-server'a JSON-RPC çağrısı yapar."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    }
    try:
        result = subprocess.run(
            ["npx", "-y", "notebooklm-mcp-server", "server"],
            input=json.dumps(request) + "\n",
            capture_output=True,
            text=True,
            timeout=30,
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return {"error": result.stderr or "Yanıt alınamadı"}
    except subprocess.TimeoutExpired:
        return {"error": "Zaman aşımı (30s) — notebooklm-mcp-server yanıt vermedi"}
    except FileNotFoundError:
        return {"error": "npx bulunamadı — Node.js kurulu mu?"}


def add_url_source(url: str, notebook_id: str = None) -> dict:
    """Not defterine URL kaynağı ekle."""
    nb_id = notebook_id or NOTEBOOK_ID
    resp = _mcp_call("add_source", {"notebookId": nb_id, "source": url, "type": "url"})
    return {"success": "error" not in resp, "notebook_id": nb_id, "url": url, "response": resp}


def add_text_source(text: str, title: str = "Metin Kaynağı", notebook_id: str = None) -> dict:
    """Not defterine metin kaynağı ekle."""
    nb_id = notebook_id or NOTEBOOK_ID
    resp = _mcp_call("add_source", {"notebookId": nb_id, "source": text, "type": "text", "title": title})
    return {"success": "error" not in resp, "notebook_id": nb_id, "title": title, "response": resp}


def query_notebook(question: str, notebook_id: str = None) -> dict:
    """Not defterine soru sor."""
    nb_id = notebook_id or NOTEBOOK_ID
    resp = _mcp_call("query_notebook", {"notebookId": nb_id, "query": question})
    answer = ""
    if "result" in resp:
        content = resp["result"].get("content", [])
        answer = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return {"success": "error" not in resp, "notebook_id": nb_id, "question": question, "answer": answer, "response": resp}


def list_notebooks() -> dict:
    """Tüm not defterlerini listele."""
    resp = _mcp_call("list_notebooks", {})
    notebooks = []
    if "result" in resp:
        content = resp["result"].get("content", [])
        for c in content:
            if isinstance(c, dict) and c.get("text"):
                try:
                    notebooks = json.loads(c["text"])
                except Exception:
                    notebooks = [{"raw": c["text"]}]
    return {"success": "error" not in resp, "notebooks": notebooks, "response": resp}


def get_notebook_info(notebook_id: str = None) -> dict:
    """Belirli bir not defterinin bilgilerini al."""
    nb_id = notebook_id or NOTEBOOK_ID
    return {
        "notebook_id": nb_id,
        "notebook_url": f"https://notebooklm.google.com/notebook/{nb_id}",
        "default": nb_id == NOTEBOOK_ID,
    }
