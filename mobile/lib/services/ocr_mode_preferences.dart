import 'package:shared_preferences/shared_preferences.dart';

import '../models/ocr_mode.dart';

/// Kullanicinin OCR mod tercihini kalici saklar (varsayilan: fast).
class OcrModePreferences {
  OcrModePreferences({SharedPreferences? prefs}) : _prefs = prefs;

  static const prefsKey = 'ocr_mode';

  SharedPreferences? _prefs;

  Future<SharedPreferences> _ensurePrefs() async {
    return _prefs ??= await SharedPreferences.getInstance();
  }

  Future<OcrMode> load() async {
    final prefs = await _ensurePrefs();
    return OcrMode.fromApiValue(prefs.getString(prefsKey));
  }

  Future<void> save(OcrMode mode) async {
    final prefs = await _ensurePrefs();
    await prefs.setString(prefsKey, mode.apiValue);
  }
}
