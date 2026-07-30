/// Uygulama sabitleri. API entegrasyonu Phase 17'de kullanilacak.
class AppConfig {
  AppConfig._();

  static const String appName = 'Ilac Kutusu Tanima';

  /// Android emulator icin host makine localhost adresi.
  /// Fiziksel cihazda gelistirme makinesinin LAN IP'si ile override edilebilir.
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static const String analyzeEndpoint = '/api/v1/analyze';

  static const Duration splashDuration = Duration(seconds: 2);
}
