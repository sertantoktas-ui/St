# Arama ve Not Yönetimi — SOP

## Amaç
Kullanıcının notlarını kaydetmek, listelemek ve silmek; arama geçmişini takip etmek.

## Girdiler
### Not İşlemleri
- `action`: `add_note` | `list_notes` | `delete_note` | `search_notes`
- `content`: Not içeriği
- `note_id`: Silinecek notun ID'si
- `query`: Arama terimi

### Arama Geçmişi
- `action`: `save_search` | `get_history`
- `query`: Arama sorgusu
- `results`: Arama sonuçları (JSON string)
- `limit`: Kaç kayıt döndürülsün (varsayılan: 10)

## Kullanılacak Script
`execution/search_operations.py`

## Akış
### Not Ekleme
1. `search_operations.add_note(content)` çağır.
2. Dönen note_id'yi kullanıcıya göster.

### Not Listeleme
1. `search_operations.list_notes()` çağır.
2. Tarih sırasına göre göster.

### Not Arama
1. `search_operations.search_notes(query)` çağır.
2. İçerikte `query` geçen notları döndür.

### Arama Geçmişi
1. `search_operations.save_search(query, results)` ile kaydet.
2. `search_operations.get_search_history(limit)` ile listele.

## Çıktılar
- Note ID (ekleme)
- Not listesi (listeleme/arama)
- Arama geçmişi listesi

## Edge Cases
- Boş içerikli not eklenmeye çalışılırsa hata döndür.
- Arama terimi bulunamazsa boş liste döndür, hata değil.
