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
    this.failureReason,
    this.hint,
    this.matchSource = 'ocr',
    this.barcode,
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
  final String? failureReason;
  final String? hint;
  final String matchSource;
  final String? barcode;

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
      failureReason: json['failure_reason'] as String?,
      hint: json['hint'] as String?,
      matchSource: json['match_source'] as String? ?? 'ocr',
      barcode: json['barcode'] as String?,
    );
  }

  bool get isMatched => status == 'matched';

  /// Kullaniciya gosterilecek aciklama (hint varsa onu tercih et).
  String get userMessage {
    final tip = hint?.trim();
    if (tip != null && tip.isNotEmpty) {
      return tip;
    }
    return displayMessage;
  }

  String? get activeIngredient => medicine?['active_ingredient'];

  String? get dosage => medicine?['dosage'];

  String? get form => medicine?['form'];

  String? get category => medicine?['category'];

  String? get medicineId => medicine?['medicine_id'];

  Map<String, dynamic> toJson() {
    return {
      'box_index': boxIndex,
      'yolo_confidence': yoloConfidence,
      'matching_score': matchingScore,
      'status': status,
      'display_message': displayMessage,
      if (ocrText != null) 'ocr_text': ocrText,
      if (medicineName != null) 'medicine_name': medicineName,
      if (bestCandidate != null) 'best_candidate': bestCandidate,
      if (error != null) 'error': error,
      if (medicine != null) 'medicine': medicine,
      if (failureReason != null) 'failure_reason': failureReason,
      if (hint != null) 'hint': hint,
      'match_source': matchSource,
      if (barcode != null) 'barcode': barcode,
    };
  }
}
