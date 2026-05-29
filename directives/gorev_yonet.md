# Görev Yönetimi — SOP

## Amaç
Kullanıcının görevlerini oluşturmak, listelemek, tamamlamak ve silmek.

## Girdiler
- `action`: `add` | `list` | `complete` | `delete`
- `title`: Görev başlığı (add/complete/delete için)
- `description`: Görev açıklaması (opsiyonel)
- `priority`: `low` | `medium` | `high` (varsayılan: medium)
- `status_filter`: `pending` | `completed` | `all` (list için)

## Kullanılacak Script
`execution/task_operations.py`

## Akış
### Görev Ekleme
1. `task_operations.add_task(title, description, priority)` çağır.
2. Dönen task_id'yi kullanıcıya göster.

### Görev Listeleme
1. `task_operations.get_tasks(status)` çağır.
2. Önceliğe göre sırala ve göster.

### Görev Tamamlama
1. `task_operations.complete_task(task_id)` çağır.
2. `completed_at` timestamp'i DB'ye yaz.

### Görev Silme
1. `task_operations.delete_task(task_id)` çağır.

## Çıktılar
- Task ID (ekleme)
- Görev listesi (listeleme)
- Başarı/Hata durumu (tamamlama/silme)

## Edge Cases
- Aynı başlıkta birden fazla görev olabilir; ID ile işlem yap.
- Tamamlanmış görevi tekrar tamamlamaya çalışma.
