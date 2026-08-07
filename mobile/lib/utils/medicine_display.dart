import '../l10n/app_localizations.dart';

/// Veritabani placeholder ve bos alanlari kullaniciya uygun metne cevirir.
class MedicineDisplay {
  MedicineDisplay._();

  static const String unverifiedPlaceholder = 'VERIFY_FROM_OFFICIAL_LEAFLET';

  static String? formatField(String? value, {required AppStrings strings}) {
    if (value == null || value.trim().isEmpty) {
      return null;
    }
    if (value == unverifiedPlaceholder) {
      return strings.verifyFromLeaflet;
    }
    return value;
  }

  static bool shouldShowField(String? value, {required AppStrings strings}) =>
      formatField(value, strings: strings) != null;

  /// Backend 1-tabanli `box_index` dondurur.
  static String boxLabel(int boxIndex, {required AppStrings strings}) =>
      strings.boxLabelFor(boxIndex);
}
