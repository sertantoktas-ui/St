"""
Tool executor — Claude'dan gelen tool_use bloklarını execution scriptlerine yönlendirir.
Hem streamlit_app.py hem mcp_server.py tarafından kullanılır.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import execution.task_operations as tasks
import execution.email_operations as emails
import execution.report_operations as reports
import execution.search_operations as notes_svc


def execute(tool_name: str, tool_input: dict) -> str:
    """Tool adı ve input'u alır, string sonuç döndürür."""
    try:
        if tool_name == "add_task":
            r = tasks.add_task(
                tool_input["title"],
                tool_input.get("description", ""),
                tool_input.get("priority", "medium"),
            )
            return f"✅ Görev eklendi — ID: {r['task_id']}, başlık: {r['title']}, öncelik: {r['priority']}"

        elif tool_name == "list_tasks":
            status = tool_input.get("status", "pending")
            task_list = tasks.get_tasks(status)
            if not task_list:
                return f"📋 {status} görev yok."
            lines = [f"📋 {status.upper()} GÖREVLER ({len(task_list)} adet):"]
            for t in task_list:
                lines.append(f"  [{t['id']}] [{t['priority'].upper()}] {t['title']}")
            return "\n".join(lines)

        elif tool_name == "complete_task":
            r = tasks.complete_task(tool_input["task_id"])
            return f"✅ Görev {tool_input['task_id']} tamamlandı." if r["success"] else f"❌ Görev bulunamadı."

        elif tool_name == "save_email":
            send_now = tool_input.get("send_now", False)
            tone = tool_input.get("tone", "formal")
            if send_now:
                r = emails.save_and_send(tool_input["recipient"], tool_input["subject"], tool_input["body"], tone)
                status = "gönderildi ✅" if r["sent"] else f"taslak kaydedildi (SMTP hata: {r.get('send_error','')})"
            else:
                r = emails.save_email(tool_input["recipient"], tool_input["subject"], tool_input["body"], tone)
                status = "taslak kaydedildi 💾"
            return f"📧 Email {status} — ID: {r['email_id']}"

        elif tool_name == "create_report":
            r = reports.save_and_generate(tool_input["title"], tool_input["content"])
            pdf_info = f", PDF: {r['pdf_path']}" if r["pdf_path"] else f" (PDF hatası: {r.get('pdf_error','')})"
            return f"📄 Rapor oluşturuldu — ID: {r['report_id']}{pdf_info}"

        elif tool_name == "add_note":
            r = notes_svc.add_note(tool_input["content"])
            return f"📝 Not kaydedildi — ID: {r['note_id']}" if r["success"] else f"❌ {r['error']}"

        elif tool_name == "list_notes":
            query = tool_input.get("search", "")
            note_list = notes_svc.search_notes(query) if query else notes_svc.list_notes()
            if not note_list:
                return "📭 Not yok."
            lines = [f"📝 NOTLAR ({len(note_list)} adet):"]
            for n in note_list:
                preview = n["content"][:80] + ("..." if len(n["content"]) > 80 else "")
                lines.append(f"  [{n['id']}] {preview}")
            return "\n".join(lines)

        elif tool_name == "get_statistics":
            s = tasks.get_statistics()
            return (
                f"📊 İSTATİSTİKLER\n"
                f"  Görev (bekleyen/tamamlanan): {s['pending_tasks']} / {s['completed_tasks']}\n"
                f"  Email (gönderilen/taslak): {s['sent_emails']} / {s['unsent_emails']}\n"
                f"  Rapor: {s['total_reports']}\n"
                f"  Not: {len(notes_svc.list_notes())}"
            )

        else:
            return f"❌ Bilinmeyen araç: {tool_name}"

    except Exception as e:
        return f"❌ Araç hatası ({tool_name}): {e}"
