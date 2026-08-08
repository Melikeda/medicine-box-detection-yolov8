import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:medicine_box_app/models/analyze_response.dart';
import 'package:medicine_box_app/models/analyze_summary.dart';
import 'package:medicine_box_app/models/medicine_box_result.dart';
import 'package:medicine_box_app/services/scan_api_service.dart';

void main() {
  AnalyzeResponse sampleResponse() {
    return const AnalyzeResponse(
      success: true,
      detectionCount: 1,
      medicines: [
        MedicineBoxResult(
          boxIndex: 0,
          yoloConfidence: 0.9,
          matchingScore: 0.95,
          status: 'matched',
          displayMessage: 'Parol',
          medicineName: 'Parol',
        ),
      ],
      summary: AnalyzeSummary(matchedCount: 1),
      ocrMode: 'fast',
      processingTimeMs: 1000,
      filename: 'box.jpg',
    );
  }

  test('createScan posts analyze payload and returns server id', () async {
    final client = MockClient((request) async {
      expect(request.url.path, '/api/v1/scans');
      expect(request.method, 'POST');
      final body = jsonDecode(request.body) as Map<String, dynamic>;
      expect(body['response']['success'], isTrue);
      expect(body['response']['filename'], 'box.jpg');
      return http.Response(
        jsonEncode({
          'success': true,
          'scan': {
            'id': 42,
            'created_at': '2026-08-08T00:00:00+00:00',
            'detection_count': 1,
            'matched_count': 1,
            'preview_label': 'Parol',
            'response': body['response'],
          },
        }),
        201,
        headers: {'content-type': 'application/json'},
      );
    });

    final service = ScanApiService(
      client: client,
      baseUrl: 'http://example.com',
    );
    final id = await service.createScan(response: sampleResponse());
    expect(id, 42);
  });

  test('createScan skips unsuccessful responses', () async {
    var called = false;
    final client = MockClient((request) async {
      called = true;
      return http.Response('{}', 500);
    });
    final service = ScanApiService(
      client: client,
      baseUrl: 'http://example.com',
    );
    final id = await service.createScan(
      response: const AnalyzeResponse(
        success: false,
        detectionCount: 0,
        medicines: [],
        summary: AnalyzeSummary(),
        ocrMode: 'fast',
        processingTimeMs: 0,
      ),
    );
    expect(id, isNull);
    expect(called, isFalse);
  });
}
