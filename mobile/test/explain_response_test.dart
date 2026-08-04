import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/models/explain_response.dart';

void main() {
  test('ExplainResponse.fromJson parses API payload', () {
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
    expect(response.disclaimer, isNotEmpty);
    expect(response.provider, 'gemini');
  });
}
