"""
Merkezi araç tanımları — Claude Tool Use ve MCP Server ikisi de buradan okur.
"""

TOOLS = [
    {
        "name": "add_task",
        "description": "Yeni görev ekle",
        "input_schema": {
            "type": "object",
            "properties": {
                "title":       {"type": "string", "description": "Görev başlığı"},
                "description": {"type": "string", "description": "Açıklama (opsiyonel)"},
                "priority":    {"type": "string", "enum": ["low", "medium", "high"], "description": "Öncelik"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "list_tasks",
        "description": "Bekleyen görevleri listele",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pending", "completed"], "description": "Görev durumu"},
            },
        },
    },
    {
        "name": "complete_task",
        "description": "Görevi tamamlandı olarak işaretle",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Görev ID'si"},
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "save_email",
        "description": "Email taslağı oluştur ve veritabanına kaydet",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "Alıcı email adresi"},
                "subject":   {"type": "string", "description": "Email konusu"},
                "body":      {"type": "string", "description": "Email içeriği"},
                "tone":      {"type": "string", "enum": ["formal", "casual", "friendly"]},
                "send_now":  {"type": "boolean", "description": "Hemen gönder (SMTP gerekli)"},
            },
            "required": ["recipient", "subject", "body"],
        },
    },
    {
        "name": "create_report",
        "description": "Rapor oluştur ve PDF olarak kaydet",
        "input_schema": {
            "type": "object",
            "properties": {
                "title":   {"type": "string", "description": "Rapor başlığı"},
                "content": {"type": "string", "description": "Rapor içeriği"},
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "add_note",
        "description": "Not ekle",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Not içeriği"},
            },
            "required": ["content"],
        },
    },
    {
        "name": "list_notes",
        "description": "Kayıtlı notları listele",
        "input_schema": {
            "type": "object",
            "properties": {
                "search": {"type": "string", "description": "Arama terimi (opsiyonel)"},
            },
        },
    },
    {
        "name": "get_statistics",
        "description": "Asistan istatistiklerini göster (görev, email, rapor sayıları)",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "notebooklm_add_source",
        "description": "Google NotebookLM not defterine kaynak ekle (URL veya metin)",
        "input_schema": {
            "type": "object",
            "properties": {
                "source":      {"type": "string", "description": "URL veya metin içeriği"},
                "source_type": {"type": "string", "enum": ["url", "text"], "description": "Kaynak türü"},
                "title":       {"type": "string", "description": "Metin kaynağı için başlık (opsiyonel)"},
                "notebook_id": {"type": "string", "description": "Notebook ID (boş bırakırsan varsayılan kullanılır)"},
            },
            "required": ["source", "source_type"],
        },
    },
    {
        "name": "notebooklm_query",
        "description": "Google NotebookLM not defterine soru sor, kaynaklar üzerinden yanıt al",
        "input_schema": {
            "type": "object",
            "properties": {
                "question":    {"type": "string", "description": "Sorulacak soru"},
                "notebook_id": {"type": "string", "description": "Notebook ID (boş bırakırsan varsayılan kullanılır)"},
            },
            "required": ["question"],
        },
    },
    {
        "name": "notebooklm_list",
        "description": "Google NotebookLM'deki tüm not defterlerini listele",
        "input_schema": {"type": "object", "properties": {}},
    },
]
