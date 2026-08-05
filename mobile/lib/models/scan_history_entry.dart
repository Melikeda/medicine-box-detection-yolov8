import 'analyze_response.dart';

/// Yerel tarama gecmisi listesi icin hafif kayit modeli.
class ScanHistoryEntry {
  const ScanHistoryEntry({
    required this.id,
    required this.createdAt,
    required this.detectionCount,
    required this.matchedCount,
    required this.previewLabel,
    required this.response,
    this.imagePath,
  });

  final int id;
  final DateTime createdAt;
  final int detectionCount;
  final int matchedCount;
  final String previewLabel;
  final String? imagePath;
  final AnalyzeResponse response;

  String get subtitle =>
      '$detectionCount kutu · $matchedCount eslesti · '
      '${createdAt.day.toString().padLeft(2, '0')}.'
      '${createdAt.month.toString().padLeft(2, '0')}.'
      '${createdAt.year} '
      '${createdAt.hour.toString().padLeft(2, '0')}:'
      '${createdAt.minute.toString().padLeft(2, '0')}';
}
