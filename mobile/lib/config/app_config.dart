/// Uygulama sabitleri ve FastAPI baglanti ayarlari.
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

  static const String healthEndpoint = '/health';

  /// CPU uzerinde OCR (fast mod, ~4 varyant + erken cikis) dakikalarca surebilir.
  static const Duration analyzeTimeout = Duration(seconds: 300);

  static const Duration healthTimeout = Duration(seconds: 10);

  static String get analyzeUrl => '$apiBaseUrl$analyzeEndpoint';

  static String get healthUrl => '$apiBaseUrl$healthEndpoint';

  static const Duration splashDuration = Duration(seconds: 2);
}
