import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/l10n/app_localizations.dart';
import 'package:medicine_box_app/models/explain_response.dart';

void main() {
  test('ExplainResponse.fromJson parses legacy API payload', () {
    final response = ExplainResponse.fromJson({
      'success': true,
      'medicine_id': 'MED001',
      'medicine_name': 'Parol',
      'explanation': 'Parol, agri kesici bir ilactir.',
      'disclaimer': 'Bu aciklama tibbi tavsiye degildir.',
      'cached': false,
      'provider': 'gemini',
      'model': 'gemini-2.5-flash',
    });

    expect(response.success, isTrue);
    expect(response.medicineId, 'MED001');
    expect(response.explanation, contains('Parol'));
    expect(response.summary, contains('Parol'));
    expect(response.disclaimer, isNotEmpty);
    expect(response.provider, 'gemini');
  });

  test('ExplainResponse.fromJson parses structured API payload', () {
    final response = ExplainResponse.fromJson({
      'success': true,
      'medicine_id': 'MED020',
      'medicine_name': 'Etol Fort',
      'explanation': 'Etol Fort ozet. Kullanim.',
      'summary': 'Etol Fort, etodolak iceren bir ilactir.',
      'usage': 'Kas-iskelet kaynakli bazi durumlarda kullanilabilir.',
      'commonUses': [
        'Eklem kaynakli bazi agri durumlari',
        'Kas-iskelet sistemi agri durumlari',
      ],
      'warnings': ['Doktora danisin.'],
      'activeIngredient': 'Etodolac',
      'dose': '400 MG',
      'form': 'Film Coated Tablet',
      'category': 'Kas ve Eklem',
      'disclaimer': 'Kisisel tibbi oneri yerine gecmez.',
      'cached': false,
      'provider': 'mock',
      'model': 'mock',
      'structured': {
        'summary': 'Etol Fort, etodolak iceren bir ilactir.',
        'usage': 'Kas-iskelet kaynakli bazi durumlarda kullanilabilir.',
        'commonUses': [
          'Eklem kaynakli bazi agri durumlari',
          'Kas-iskelet sistemi agri durumlari',
        ],
        'warnings': ['Doktora danisin.'],
      },
    });

    expect(response.summary, contains('Etol Fort'));
    expect(response.usage, contains('Kas-iskelet'));
    expect(response.commonUses, hasLength(2));
    expect(response.warnings, contains('Doktora danisin.'));
    expect(response.hasStructuredContent, isTrue);
    expect(response.category, 'Kas ve Eklem');
  });

  test('ExplainResponse.catalogFallback builds catalog text without API', () {
    final response = ExplainResponse.catalogFallback(
      medicineId: 'MED001',
      medicineName: 'Parol',
      category: 'Ağrı Kesici',
      activeIngredient: 'Paracetamol',
      strings: AppStrings.of(AppLanguage.tr),
    );

    expect(response.success, isTrue);
    expect(response.provider, 'catalog-fallback');
    expect(response.summary, contains('Parol'));
    expect(response.summary, contains('Paracetamol'));
    expect(response.warnings, isNotEmpty);
  });
}
