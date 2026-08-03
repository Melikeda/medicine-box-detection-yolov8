/// API / network failures surfaced to the UI layer.
class AnalyzeApiException implements Exception {
  AnalyzeApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}
