import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/l10n/app_localizations.dart';
import 'package:medicine_box_app/models/analyze_response.dart';
import 'package:medicine_box_app/models/analyze_summary.dart';
import 'package:medicine_box_app/models/medicine_box_result.dart';
import 'package:medicine_box_app/screens/result_screen.dart';

Widget _wrap(Widget child) {
  final locale = LocaleController();
  return LocaleScope(
    controller: locale,
    child: ListenableBuilder(
      listenable: locale,
      builder: (context, _) => MaterialApp(home: child),
    ),
  );
}

void main() {
  testWidgets('Result screen shows summary and medicine card', (tester) async {
    const response = AnalyzeResponse(
      success: true,
      detectionCount: 1,
      medicines: [
        MedicineBoxResult(
          boxIndex: 1,
          yoloConfidence: 0.9,
          matchingScore: 88.0,
          status: 'matched',
          displayMessage: 'Parol 500 mg eslesti.',
          medicineName: 'Parol 500 mg',
          medicine: {
            'active_ingredient': 'VERIFY_FROM_OFFICIAL_LEAFLET',
            'dosage': '500 mg',
          },
        ),
      ],
      summary: AnalyzeSummary(matchedCount: 1),
      ocrMode: 'fast',
      processingTimeMs: 2500,
    );

    await tester.pumpWidget(
      _wrap(const ResultScreen(response: response)),
    );
    await tester.pump();

    expect(find.text('Analiz Sonucu'), findsOneWidget);
    expect(find.text('Eşleşti: 1'), findsOneWidget);
    expect(find.text('Kutu 1'), findsOneWidget);
    expect(find.text('Parol 500 mg'), findsOneWidget);
    expect(
      find.text('Resmi ürün bilgisinden doğrulanmalı'),
      findsOneWidget,
    );
    expect(find.text('500 mg'), findsOneWidget);
  });
}
