import 'analyze_summary.dart';
import 'medicine_box_result.dart';

class AnalyzeResponse {
  const AnalyzeResponse({
    required this.success,
    required this.detectionCount,
    required this.medicines,
    required this.summary,
    required this.ocrMode,
    required this.processingTimeMs,
    this.filename,
    this.medicinesCompared = 0,
    this.error,
    this.disclaimer,
  });

  final bool success;
  final String? filename;
  final int detectionCount;
  final List<MedicineBoxResult> medicines;
  final int medicinesCompared;
  final String? error;
  final AnalyzeSummary summary;
  final String ocrMode;
  final double processingTimeMs;
  final String? disclaimer;

  factory AnalyzeResponse.fromJson(Map<String, dynamic> json) {
    final medicinesJson = json['medicines'];
    final medicines = medicinesJson is List
        ? medicinesJson
            .whereType<Map<String, dynamic>>()
            .map(MedicineBoxResult.fromJson)
            .toList()
        : <MedicineBoxResult>[];

    final summaryJson = json['summary'];
    final summary = summaryJson is Map<String, dynamic>
        ? AnalyzeSummary.fromJson(summaryJson)
        : const AnalyzeSummary();

    return AnalyzeResponse(
      success: json['success'] as bool? ?? false,
      filename: json['filename'] as String?,
      detectionCount: json['detection_count'] as int? ?? 0,
      medicines: medicines,
      medicinesCompared: json['medicines_compared'] as int? ?? 0,
      error: json['error'] as String?,
      summary: summary,
      ocrMode: json['ocr_mode'] as String? ?? 'fast',
      processingTimeMs: (json['processing_time_ms'] as num?)?.toDouble() ?? 0,
      disclaimer: json['disclaimer'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      if (filename != null) 'filename': filename,
      'detection_count': detectionCount,
      'medicines': medicines.map((item) => item.toJson()).toList(),
      'medicines_compared': medicinesCompared,
      if (error != null) 'error': error,
      'summary': summary.toJson(),
      'ocr_mode': ocrMode,
      'processing_time_ms': processingTimeMs,
      if (disclaimer != null) 'disclaimer': disclaimer,
    };
  }
}
