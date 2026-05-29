# MCP Entegrasyonu — SOP

## Amaç
Kişisel Asistanı hem bir MCP server olarak dışa açmak hem de Claude Tool Use ile sohbette araç çağrısı yapmak.

## Bileşenler

### 1. Claude Tool Use (L2 → L3)
- `execution/tools_config.py` — araç tanımları (tek kaynak)
- `execution/tool_executor.py` — araç adı → execution script yönlendirmesi
- `streamlit_app.py` — sohbet sırasında `stop_reason == "tool_use"` döngüsü

**Araçlar:** `add_task`, `list_tasks`, `complete_task`, `save_email`, `create_report`, `add_note`, `list_notes`, `get_statistics`

### 2. MCP Server (stdio)
- `execution/mcp_server.py` — FastMCP tabanlı stdio server
- Başlatma: `python execution/mcp_server.py`
- `.mcp.json` ile Claude Code veya başka MCP istemcisine bağla

### 3. Dış MCP Serverlar (.mcp.json)
- `kisisel-asistan` — bu proje (stdio)
- `filesystem` — yerel dosya sistemi (@modelcontextprotocol/server-filesystem)
- `fetch` — web sayfası çekme (mcp-server-fetch)

## .mcp.json Kullanımı
Proje kökündeki `.mcp.json` dosyası Claude Code tarafından otomatik yüklenir.
Yeni bir server eklemek için bu dosyaya entry ekle ve direktifi güncelle.

## Edge Cases
- MCP server hata verirse `python -c "from execution.mcp_server import mcp"` ile import testi yap.
- Tool Use döngüsü sonsuz dönmemesi için max_iterations=5 eklenebilir.
- Dış serverlar (filesystem, fetch) için ilgili paketlerin yüklü olması gerekir.
