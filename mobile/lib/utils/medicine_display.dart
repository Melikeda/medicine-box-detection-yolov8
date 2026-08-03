/// Veritabani placeholder ve bos alanlari kullaniciya uygun metne cevirir.
class MedicineDisplay {
  MedicineDisplay._();

  static const String unverifiedPlaceholder = 'VERIFY_FROM_OFFICIAL_LEAFLET';

  static String? formatField(String? value) {
    if (value == null || value.trim().isEmpty) {
      return null;
    }
    if (value == unverifiedPlaceholder) {
      return 'Resmi urun bilgisinden dogrulanmali';
    }
    return value;
  }

  static bool shouldShowField(String? value) => formatField(value) != null;

  /// Backend 1-tabanli `box_index` dondurur.
  static String boxLabel(int boxIndex) => 'Kutu $boxIndex';
}
