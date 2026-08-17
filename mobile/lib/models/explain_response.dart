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
    this.summary = '',
    this.usage = '',
    this.commonUses = const [],
    this.activeIngredient,
    this.dose,
    this.form,
    this.category,
    this.warnings = const [],
  });

  final bool success;
  final String medicineId;
  final String medicineName;
  final String explanation;
  final String summary;
  final String usage;
  final List<String> commonUses;
  final String? activeIngredient;
  final String? dose;
  final String? form;
  final String? category;
  final List<String> warnings;
  final String disclaimer;
  final bool cached;
  final String provider;
  final String model;

  bool get hasStructuredContent =>
      summary.trim().isNotEmpty ||
      usage.trim().isNotEmpty ||
      commonUses.isNotEmpty ||
      warnings.isNotEmpty;

  factory ExplainResponse.fromJson(Map<String, dynamic> json) {
    final structured = json['structured'];
    final structuredMap =
        structured is Map<String, dynamic> ? structured : null;

    String readString(String key, {String fallback = ''}) {
      final top = json[key];
      if (top is String && top.trim().isNotEmpty) {
        return top;
      }
      final nested = structuredMap?[key];
      if (nested is String) {
        return nested;
      }
      return fallback;
    }

    List<String> readStringList(String key) {
      final top = json[key];
      if (top is List) {
        return top
            .whereType<Object>()
            .map((item) => item.toString().trim())
            .where((item) => item.isNotEmpty)
            .toList();
      }
      final nested = structuredMap?[key];
      if (nested is List) {
        return nested
            .whereType<Object>()
            .map((item) => item.toString().trim())
            .where((item) => item.isNotEmpty)
            .toList();
      }
      return const [];
    }

    final summary = readString('summary');
    final explanation = json['explanation'] as String? ?? '';

    return ExplainResponse(
      success: json['success'] as bool? ?? false,
      medicineId: json['medicine_id'] as String? ?? '',
      medicineName: json['medicine_name'] as String? ?? '',
      explanation: explanation,
      summary: summary.isNotEmpty ? summary : explanation,
      usage: readString('usage'),
      commonUses: readStringList('commonUses'),
      activeIngredient: _nullableString(
        json['activeIngredient'] ?? structuredMap?['activeIngredient'],
      ),
      dose: _nullableString(json['dose'] ?? structuredMap?['dose']),
      form: _nullableString(json['form'] ?? structuredMap?['form']),
      category: _nullableString(json['category'] ?? structuredMap?['category']),
      warnings: readStringList('warnings'),
      disclaimer: json['disclaimer'] as String? ?? '',
      cached: json['cached'] as bool? ?? false,
      provider: json['provider'] as String? ?? '',
      model: json['model'] as String? ?? '',
    );
  }

  factory ExplainResponse.catalogFallback({
    required String medicineId,
    required String medicineName,
    String? category,
    String? activeIngredient,
    String? dose,
    String? form,
    required String disclaimer,
  }) {
    final name = medicineName.trim().isEmpty ? 'Bu ilaç' : medicineName.trim();
    final ingredient = (activeIngredient ?? '').trim();
    final cat = (category ?? '').trim();

    late final String summary;
    if (ingredient.isNotEmpty && cat.isNotEmpty) {
      summary =
          '$name, $ingredient içeren ve $cat kategorisinde yer alan bir ilaçtır.';
    } else if (ingredient.isNotEmpty) {
      summary = '$name, $ingredient içeren bir ilaçtır.';
    } else if (cat.isNotEmpty) {
      summary = '$name, $cat kategorisinde yer alan bir ilaçtır.';
    } else {
      summary = '$name hakkında sınırlı katalog bilgisi bulunmaktadır.';
    }

    return ExplainResponse(
      success: true,
      medicineId: medicineId,
      medicineName: medicineName,
      explanation: summary,
      summary: summary,
      usage:
          'Resmi kullanım için ürün prospektüsüne ve eczacınıza danışın.',
      commonUses: const [],
      activeIngredient: _nullableString(activeIngredient),
      dose: _nullableString(dose),
      form: _nullableString(form),
      category: _nullableString(category),
      warnings: const [
        'Bu bilgiler kişisel tıbbi tavsiye yerine geçmez; doktorunuza veya eczacınıza danışın.',
        'Kullanmadan önce ürün prospektüsünü okuyun.',
      ],
      disclaimer: disclaimer,
      cached: false,
      provider: 'catalog-fallback',
      model: 'catalog-fallback',
    );
  }

  static String? _nullableString(Object? value) {
    if (value is! String) {
      return null;
    }
    final trimmed = value.trim();
    return trimmed.isEmpty ? null : trimmed;
  }
}
