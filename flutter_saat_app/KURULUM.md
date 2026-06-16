# Dünya Saati - Flutter App

## Gereksinimler

- Flutter SDK (https://flutter.dev/docs/get-started/install)
- Xcode 14+ (Mac gerekli)
- Apple Developer hesabı ($99/yıl)
- iOS 12.0+

## Kurulum

```bash
cd flutter_saat_app

# Bağımlılıkları yükle
flutter pub get

# iOS simülatörde çalıştır
flutter run -d ios

# Release build (App Store için)
flutter build ios --release
```

## App Store'a Yükleme Adımları

1. `flutter build ios --release` komutu çalıştır
2. Xcode'da `ios/Runner.xcworkspace` dosyasını aç
3. Signing & Capabilities > Team'i Apple Developer hesabınla seç
4. Product > Archive menüsünden arşiv oluştur
5. Distribute App > App Store Connect seçeneğiyle yükle
6. App Store Connect (appstoreconnect.apple.com) üzerinden incelemeye gönder

## Bağımlılıklar

- `timezone` — Dünya zaman dilimi veritabanı
- `intl` — Tarih/saat formatlaması (Türkçe dahil)
- `flutter_timezone` — Cihazın yerel saat dilimini tespit eder
