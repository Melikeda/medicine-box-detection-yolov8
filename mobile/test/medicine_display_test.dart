import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/l10n/app_localizations.dart';
import 'package:medicine_box_app/utils/medicine_display.dart';

void main() {
  final tr = AppStrings.of(AppLanguage.tr);
  final en = AppStrings.of(AppLanguage.en);

  group('MedicineDisplay', () {
    test('formatField maps unverified placeholder', () {
      expect(
        MedicineDisplay.formatField(
          MedicineDisplay.unverifiedPlaceholder,
          strings: tr,
        ),
        tr.verifyFromLeaflet,
      );
      expect(
        MedicineDisplay.formatField(
          MedicineDisplay.unverifiedPlaceholder,
          strings: en,
        ),
        en.verifyFromLeaflet,
      );
    });

    test('formatField returns null for empty values', () {
      expect(MedicineDisplay.formatField(null, strings: tr), isNull);
      expect(MedicineDisplay.formatField('', strings: tr), isNull);
      expect(MedicineDisplay.formatField('   ', strings: tr), isNull);
    });

    test('formatField passes through real values', () {
      expect(
        MedicineDisplay.formatField('Parasetamol', strings: tr),
        'Parasetamol',
      );
    });

    test('boxLabel uses backend 1-based index', () {
      expect(MedicineDisplay.boxLabel(1, strings: tr), 'Kutu 1');
      expect(MedicineDisplay.boxLabel(1, strings: en), 'Box 1');
    });
  });
}
