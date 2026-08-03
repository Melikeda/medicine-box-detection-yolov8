class AnalyzeSummary {
  const AnalyzeSummary({
    this.matchedCount = 0,
    this.notFoundCount = 0,
    this.notMedicineBoxCount = 0,
    this.errorCount = 0,
  });

  final int matchedCount;
  final int notFoundCount;
  final int notMedicineBoxCount;
  final int errorCount;

  factory AnalyzeSummary.fromJson(Map<String, dynamic> json) {
    return AnalyzeSummary(
      matchedCount: json['matched_count'] as int? ?? 0,
      notFoundCount: json['not_found_count'] as int? ?? 0,
      notMedicineBoxCount: json['not_medicine_box_count'] as int? ?? 0,
      errorCount: json['error_count'] as int? ?? 0,
    );
  }

  int get total =>
      matchedCount + notFoundCount + notMedicineBoxCount + errorCount;
}
