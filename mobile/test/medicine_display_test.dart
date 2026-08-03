import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/utils/medicine_display.dart';

void main() {
  group('MedicineDisplay', () {
    test('formatField maps unverified placeholder', () {
      expect(
        MedicineDisplay.formatField(MedicineDisplay.unverifiedPlaceholder),
        'Resmi urun bilgisinden dogrulanmali',
      );
    });

    test('formatField returns null for empty values', () {
      expect(MedicineDisplay.formatField(null), isNull);
      expect(MedicineDisplay.formatField(''), isNull);
      expect(MedicineDisplay.formatField('   '), isNull);
    });

    test('formatField passes through real values', () {
      expect(MedicineDisplay.formatField('Parasetamol'), 'Parasetamol');
    });

    test('boxLabel uses backend 1-based index', () {
      expect(MedicineDisplay.boxLabel(1), 'Kutu 1');
    });
  });
}
