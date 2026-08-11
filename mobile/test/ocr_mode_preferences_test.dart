import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:medicine_box_app/models/ocr_mode.dart';
import 'package:medicine_box_app/services/ocr_mode_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('defaults to fast when unset', () async {
    final prefs = OcrModePreferences();
    expect(await prefs.load(), OcrMode.fast);
  });

  test('persists accurate mode', () async {
    final prefs = OcrModePreferences();
    await prefs.save(OcrMode.accurate);
    expect(await prefs.load(), OcrMode.accurate);
  });

  test('fromApiValue maps unknown to fast', () {
    expect(OcrMode.fromApiValue(null), OcrMode.fast);
    expect(OcrMode.fromApiValue('nope'), OcrMode.fast);
    expect(OcrMode.fromApiValue('accurate'), OcrMode.accurate);
  });
}
