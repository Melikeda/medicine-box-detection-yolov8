import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:medicine_box_app/models/analyze_response.dart';
import 'package:medicine_box_app/models/analyze_summary.dart';
import 'package:medicine_box_app/models/medicine_box_result.dart';
import 'package:medicine_box_app/services/scan_history_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  late Directory tempDir;
  late ScanHistoryService service;

  setUp(() async {
    tempDir = await Directory.systemTemp.createTemp('scan_history_test_');
    service = ScanHistoryService(
      maxEntries: 2,
      openDatabase: () async {
        final dbPath = p.join(tempDir.path, 'test_scan_history.db');
        return databaseFactoryFfi.openDatabase(
          dbPath,
          options: OpenDatabaseOptions(
            version: 1,
            onCreate: (db, version) async {
              await db.execute('''
                CREATE TABLE scan_history (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  created_at INTEGER NOT NULL,
                  detection_count INTEGER NOT NULL,
                  matched_count INTEGER NOT NULL,
                  preview_label TEXT NOT NULL,
                  image_path TEXT,
                  response_json TEXT NOT NULL
                )
              ''');
            },
          ),
        );
      },
      documentsDirectory: () async => tempDir,
    );
  });

  tearDown(() async {
    await service.close();
    if (await tempDir.exists()) {
      try {
        await tempDir.delete(recursive: true);
      } on PathAccessException {
        // Windows may keep a brief lock after SQLite close.
      }
    }
  });

  AnalyzeResponse sampleResponse() {
    return const AnalyzeResponse(
      success: true,
      detectionCount: 1,
      medicines: [
        MedicineBoxResult(
          boxIndex: 1,
          yoloConfidence: 0.9,
          matchingScore: 95,
          status: 'matched',
          displayMessage: 'Eslesti',
          medicineName: 'Parol 500 mg',
        ),
      ],
      summary: AnalyzeSummary(matchedCount: 1),
      ocrMode: 'fast',
      processingTimeMs: 1200,
    );
  }

  test('saveScan stores entry and listScans returns it', () async {
    await service.saveScan(response: sampleResponse());

    final entries = await service.listScans();
    expect(entries, hasLength(1));
    expect(entries.first.previewLabel, 'Parol 500 mg');
    expect(entries.first.matchedCount, 1);
    expect(entries.first.response.medicines.first.medicineName, 'Parol 500 mg');
  });

  test('saveScan skips unsuccessful responses', () async {
    await service.saveScan(
      response: const AnalyzeResponse(
        success: false,
        detectionCount: 0,
        medicines: [],
        summary: AnalyzeSummary(),
        ocrMode: 'fast',
        processingTimeMs: 0,
      ),
    );

    final entries = await service.listScans();
    expect(entries, isEmpty);
  });

  test('trim keeps only maxEntries newest records', () async {
    await service.saveScan(response: sampleResponse());
    await Future<void>.delayed(const Duration(milliseconds: 5));
    await service.saveScan(
      response: const AnalyzeResponse(
        success: true,
        detectionCount: 1,
        medicines: [
          MedicineBoxResult(
            boxIndex: 1,
            yoloConfidence: 0.9,
            matchingScore: 95,
            status: 'matched',
            displayMessage: 'Eslesti',
            medicineName: 'Dolorex',
          ),
        ],
        summary: AnalyzeSummary(matchedCount: 1),
        ocrMode: 'fast',
        processingTimeMs: 900,
      ),
    );
    await Future<void>.delayed(const Duration(milliseconds: 5));
    await service.saveScan(
      response: const AnalyzeResponse(
        success: true,
        detectionCount: 1,
        medicines: [
          MedicineBoxResult(
            boxIndex: 1,
            yoloConfidence: 0.9,
            matchingScore: 95,
            status: 'matched',
            displayMessage: 'Eslesti',
            medicineName: 'A-Ferin Forte',
          ),
        ],
        summary: AnalyzeSummary(matchedCount: 1),
        ocrMode: 'fast',
        processingTimeMs: 800,
      ),
    );

    final entries = await service.listScans();
    expect(entries, hasLength(2));
    expect(entries.first.previewLabel, 'A-Ferin Forte');
    expect(entries.last.previewLabel, 'Dolorex');
  });

  test('deleteScan removes entry', () async {
    await service.saveScan(response: sampleResponse());
    final entries = await service.listScans();

    await service.deleteScan(entries.first.id);

    expect(await service.listScans(), isEmpty);
  });
}
