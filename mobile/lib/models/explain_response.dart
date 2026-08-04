class ExplainResponse {
  const ExplainResponse({
    required this.success,
    required this.medicineId,
    required this.medicineName,
    required this.explanation,
    required this.disclaimer,
    required this.cached,
    required this.provider,
    required this.model,
  });

  final bool success;
  final String medicineId;
  final String medicineName;
  final String explanation;
  final String disclaimer;
  final bool cached;
  final String provider;
  final String model;

  factory ExplainResponse.fromJson(Map<String, dynamic> json) {
    return ExplainResponse(
      success: json['success'] as bool? ?? false,
      medicineId: json['medicine_id'] as String? ?? '',
      medicineName: json['medicine_name'] as String? ?? '',
      explanation: json['explanation'] as String? ?? '',
      disclaimer: json['disclaimer'] as String? ?? '',
      cached: json['cached'] as bool? ?? false,
      provider: json['provider'] as String? ?? '',
      model: json['model'] as String? ?? '',
    );
  }
}
