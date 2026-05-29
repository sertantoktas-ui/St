# Google NotebookLM MCP Entegrasyonu — SOP

## Varsayılan Notebook
ID: `4aa95fc5-5f77-4575-afc6-4b9e6766da6f`
URL: https://notebooklm.google.com/notebook/4aa95fc5-5f77-4575-afc6-4b9e6766da6f
`.env` ve `.env.example` dosyalarında `NOTEBOOKLM_NOTEBOOK_ID` olarak kayıtlı.

## Amaç
NotebookLM'de not defteri oluşturmak, kaynak (PDF, URL, metin) eklemek ve soru sormak.

## Kullanılan Paket
`notebooklm-mcp-server` (npm) — browser otomasyonu tabanlı, Google hesabı gerektirir.

## Kurulum (Tek Seferlik)

### 1. Auth (Google Girişi)
```bash
npx notebooklm-mcp-server auth
```
Tarayıcı açılır → Google hesabınla giriş yap → oturum kaydedilir.

### 2. MCP Server Test
```bash
npx notebooklm-mcp-server server
```
Hata yoksa `stdio` modunda çalışır.

### 3. .mcp.json Kontrolü
Proje kökündeki `.mcp.json`'da `notebooklm` entry'si mevcut.
Claude Code bu dosyayı otomatik okur.

## Araçlar (MCP üzerinden)

| Araç | Açıklama |
|---|---|
| `create_notebook` | Yeni not defteri oluştur |
| `add_source` | URL, PDF veya metin kaynağı ekle |
| `query_notebook` | Not defterine soru sor |
| `list_notebooks` | Tüm not defterlerini listele |
| `delete_notebook` | Not defteri sil |

## Örnek Kullanım (Claude ile)
> "NotebookLM'de 'Proje Araştırma' adında bir not defteri oluştur ve şu URL'yi kaynak olarak ekle: ..."

> "NotebookLM'deki Proje Araştırma not defterine göre ana bulgular neler?"

## Edge Cases
- **Auth süresi dolar:** `npx notebooklm-mcp-server auth` tekrar çalıştır.
- **Browser otomasyonu:** Headless mod çalışmıyorsa `DISPLAY` ortam değişkeni gerekebilir.
- **Rate limit:** NotebookLM kısa sürede çok istek atılırsa blok koyabilir, 1-2 dakika bekle.
- **API değişimi:** Google undocumented API kullandığından güncellemeler gerekebilir. Paket versiyonunu takip et.

## Notlar
- Bu entegrasyon resmi Google API değil — community tabanlı browser otomasyon.
- NotebookLM Enterprise kullananlar için resmi API mevcuttur (Google Cloud).
