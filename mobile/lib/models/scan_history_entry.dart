import '../l10n/app_localizations.dart';
import 'analyze_response.dart';

/// Lightweight record model for the local scan history list.
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

  String subtitleFor(AppStrings strings) => strings.historySubtitle(
        detectionCount: detectionCount,
        matchedCount: matchedCount,
        createdAt: createdAt,
      );
}
