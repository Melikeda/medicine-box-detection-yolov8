/// Application constants and FastAPI connection settings.
class AppConfig {
  AppConfig._();

  static const String appName = 'Yolocilin';

  /// Host-machine localhost address for the Android emulator.
  /// Can be overridden with the development machine's LAN IP on a physical device.
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static const String analyzeEndpoint = '/api/v1/analyze';

  static const String explainEndpoint = '/api/v1/explain';

  static const String scansEndpoint = '/api/v1/scans';

  static const String barcodeLookupEndpoint = '/api/v1/barcode/lookup';

  static const String barcodeScanEndpoint = '/api/v1/barcode/scan';

  static const String healthEndpoint = '/health';

  /// CPU OCR (fast mode, ~4 variants plus early exit) can take several minutes.
  static const Duration analyzeTimeout = Duration(seconds: 300);

  static const Duration explainTimeout = Duration(seconds: 30);

  static const Duration barcodeTimeout = Duration(seconds: 30);

  static const Duration scansTimeout = Duration(seconds: 15);

  static const Duration healthTimeout = Duration(seconds: 10);

  static String get analyzeUrl => '$apiBaseUrl$analyzeEndpoint';

  static String get healthUrl => '$apiBaseUrl$healthEndpoint';

  static const Duration splashDuration = Duration(seconds: 2);
}
