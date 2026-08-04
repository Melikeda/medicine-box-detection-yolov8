class MedicineBoxResult {
  const MedicineBoxResult({
    required this.boxIndex,
    required this.yoloConfidence,
    required this.matchingScore,
    required this.status,
    required this.displayMessage,
    this.ocrText,
    this.medicineName,
    this.bestCandidate,
    this.error,
    this.medicine,
  });

  final int boxIndex;
  final double yoloConfidence;
  final double matchingScore;
  final String status;
  final String displayMessage;
  final String? ocrText;
  final String? medicineName;
  final String? bestCandidate;
  final String? error;
  final Map<String, String>? medicine;

  factory MedicineBoxResult.fromJson(Map<String, dynamic> json) {
    final rawMedicine = json['medicine'];
    Map<String, String>? medicineMap;
    if (rawMedicine is Map) {
      medicineMap = rawMedicine.map(
        (key, value) => MapEntry(key.toString(), value?.toString() ?? ''),
      );
    }

    return MedicineBoxResult(
      boxIndex: json['box_index'] as int? ?? 0,
      yoloConfidence: (json['yolo_confidence'] as num?)?.toDouble() ?? 0,
      matchingScore: (json['matching_score'] as num?)?.toDouble() ?? 0,
      status: json['status'] as String? ?? 'error',
      displayMessage: json['display_message'] as String? ?? '',
      ocrText: json['ocr_text'] as String?,
      medicineName: json['medicine_name'] as String?,
      bestCandidate: json['best_candidate'] as String?,
      error: json['error'] as String?,
      medicine: medicineMap,
    );
  }

  bool get isMatched => status == 'matched';

  String? get activeIngredient => medicine?['active_ingredient'];

  String? get dosage => medicine?['dosage'];

  String? get form => medicine?['form'];

  String? get category => medicine?['category'];

  String? get medicineId => medicine?['medicine_id'];
}
