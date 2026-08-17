import '../l10n/app_localizations.dart';

/// Map database placeholders and empty fields to user-facing text.
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

  /// Backend returns a 1-based `box_index`.
  static String boxLabel(int boxIndex, {required AppStrings strings}) =>
      strings.boxLabelFor(boxIndex);
}
