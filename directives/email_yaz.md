# Email Yazma ve Gönderme — SOP

## Amaç
Kullanıcı adına profesyonel ya da kişisel email taslakları oluşturmak, veritabanına kaydetmek ve isteğe bağlı olarak SMTP üzerinden göndermek.

## Girdiler
- `recipient`: Alıcı email adresi
- `subject`: Email konusu
- `body`: Email gövdesi
- `tone`: `formal` | `casual` | `friendly`
- `send_now`: `true` | `false` (varsayılan: false)

## Kullanılacak Script
`execution/email_operations.py`

## Akış
1. Kullanıcıdan alıcı, konu, içerik ve ton bilgisini al.
2. `email_operations.save_email()` ile veritabanına kaydet.
3. `send_now=True` ise ve SMTP yapılandırılmışsa `email_operations.send_email()` çağır.
4. DB'yi `mark_sent()` ile güncelle.
5. Sonucu kullanıcıya raporla.

## Çıktılar
- Email ID (DB kaydı)
- Gönderim durumu (başarılı / başarısız / taslak olarak kaydedildi)

## Edge Cases
- SMTP bilgileri eksikse: email taslak olarak kaydedilir, hata fırlatılmaz.
- Alıcı adresi geçersizse: `email_operations.py` hata döndürür, UI'da uyarı göster.

## Öğrenilen Kısıtlar
- Gmail için uygulama şifresi (App Password) gereklidir; normal şifre çalışmaz.
- SMTP_SERVER=smtp.gmail.com, SMTP_PORT=587
