/// Backend `POST /analyze?mode=` degerleri (fast | accurate).
enum OcrMode {
  fast('fast'),
  accurate('accurate');

  const OcrMode(this.apiValue);

  final String apiValue;

  static OcrMode fromApiValue(String? raw) {
    if (raw == accurate.apiValue) {
      return OcrMode.accurate;
    }
    return OcrMode.fast;
  }
}
