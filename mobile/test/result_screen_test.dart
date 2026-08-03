import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/models/analyze_response.dart';
import 'package:medicine_box_app/models/analyze_summary.dart';
import 'package:medicine_box_app/models/medicine_box_result.dart';
import 'package:medicine_box_app/screens/result_screen.dart';

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
      const MaterialApp(
        home: ResultScreen(response: response),
      ),
    );

    expect(find.text('Analiz Sonucu'), findsOneWidget);
    expect(find.text('Eslesti: 1'), findsOneWidget);
    expect(find.text('Kutu 1'), findsOneWidget);
    expect(find.text('Parol 500 mg'), findsOneWidget);
    expect(
      find.text('Resmi urun bilgisinden dogrulanmali'),
      findsOneWidget,
    );
    expect(find.text('500 mg'), findsOneWidget);
  });
}
