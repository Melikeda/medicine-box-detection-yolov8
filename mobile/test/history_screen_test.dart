import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/models/analyze_response.dart';
import 'package:medicine_box_app/models/analyze_summary.dart';
import 'package:medicine_box_app/models/medicine_box_result.dart';
import 'package:medicine_box_app/models/scan_history_entry.dart';
import 'package:medicine_box_app/screens/history_screen.dart';
import 'package:medicine_box_app/services/scan_history_service.dart';

class _FakeHistoryService extends ScanHistoryService {
  _FakeHistoryService(this.entries);

  final List<ScanHistoryEntry> entries;

  @override
  Future<List<ScanHistoryEntry>> listScans({int? limit}) async => entries;
}

void main() {
  testWidgets('History screen shows empty state', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: HistoryScreen(
          historyService: _FakeHistoryService(const []),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Tarama Gecmisi'), findsOneWidget);
    expect(find.text('Henuz kayit yok'), findsOneWidget);
  });

  testWidgets('History screen lists saved scans', (tester) async {
    final entries = [
      ScanHistoryEntry(
        id: 1,
        createdAt: DateTime(2026, 8, 5, 18, 30),
        detectionCount: 2,
        matchedCount: 2,
        previewLabel: 'A-Ferin Forte, Dolorex',
        response: const AnalyzeResponse(
          success: true,
          detectionCount: 2,
          medicines: [
            MedicineBoxResult(
              boxIndex: 1,
              yoloConfidence: 0.9,
              matchingScore: 92,
              status: 'matched',
              displayMessage: 'Eslesti',
              medicineName: 'A-Ferin Forte',
            ),
          ],
          summary: AnalyzeSummary(matchedCount: 2),
          ocrMode: 'fast',
          processingTimeMs: 24000,
        ),
      ),
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: HistoryScreen(
          historyService: _FakeHistoryService(entries),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('A-Ferin Forte, Dolorex'), findsOneWidget);
    expect(find.textContaining('2 kutu'), findsOneWidget);
  });
}
