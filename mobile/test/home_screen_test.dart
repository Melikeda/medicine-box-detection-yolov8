import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:medicine_box_app/l10n/app_localizations.dart';
import 'package:medicine_box_app/screens/home_screen.dart';

Widget _wrap(Widget child, {LocaleController? controller}) {
  final locale = controller ?? LocaleController();
  return LocaleScope(
    controller: locale,
    child: ListenableBuilder(
      listenable: locale,
      builder: (context, _) => MaterialApp(home: child),
    ),
  );
}

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('Home shell shows welcome and bottom navigation', (tester) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_wrap(const HomeScreen()));
    await tester.pump();

    expect(find.text('Yolocilin'), findsWidgets);
    expect(find.text('Hoş Geldiniz'), findsOneWidget);
    expect(find.text('Taramaya Başla'), findsOneWidget);
    expect(find.textContaining('Uyarı:'), findsOneWidget);
    expect(find.text('Ana Sayfa'), findsOneWidget);
    expect(find.text('Tara'), findsOneWidget);
    expect(find.text('Geçmiş'), findsOneWidget);
    expect(find.text('TR'), findsWidgets);
    expect(find.text('EN'), findsWidgets);
  });

  testWidgets('Language toggle switches welcome text to English', (tester) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final locale = LocaleController();
    await tester.pumpWidget(_wrap(const HomeScreen(), controller: locale));
    await tester.pump();

    await tester.tap(find.text('EN'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    // SharedPreferences is async; allow language apply.
    await tester.pump(const Duration(milliseconds: 50));

    expect(find.text('Welcome'), findsOneWidget);
    expect(find.text('Start Scanning'), findsOneWidget);
    expect(find.text('Home'), findsOneWidget);
    expect(find.text('Scan'), findsOneWidget);
    expect(find.text('History'), findsOneWidget);
  });

  testWidgets('Scan tab opens from bottom navigation', (tester) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_wrap(const HomeScreen()));
    await tester.pump();
    await tester.tap(find.text('Tara'));
    await tester.pump();

    expect(find.text('Hızlı İlaç Tarama'), findsOneWidget);
    expect(find.text('Kamerayı Dene'), findsOneWidget);
    expect(find.text('Galeriden Seç'), findsOneWidget);
  });
}
