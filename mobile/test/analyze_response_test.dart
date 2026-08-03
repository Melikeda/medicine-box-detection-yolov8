import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/models/analyze_response.dart';
import 'package:medicine_box_app/models/analyze_summary.dart';
import 'package:medicine_box_app/models/medicine_box_result.dart';

void main() {
  group('AnalyzeSummary', () {
    test('fromJson parses summary counts', () {
      final summary = AnalyzeSummary.fromJson({
        'matched_count': 2,
        'not_found_count': 1,
        'not_medicine_box_count': 0,
        'error_count': 0,
      });

      expect(summary.matchedCount, 2);
      expect(summary.notFoundCount, 1);
      expect(summary.total, 3);
    });
  });

  group('MedicineBoxResult', () {
    test('fromJson parses matched medicine details', () {
      final result = MedicineBoxResult.fromJson({
        'box_index': 0,
        'yolo_confidence': 0.91,
        'matching_score': 87.5,
        'status': 'matched',
        'display_message': 'Ilac eslesti.',
        'medicine_name': 'Parol 500 mg',
        'ocr_text': 'PAROL 500',
        'medicine': {
          'active_ingredient': 'Parasetamol',
          'dosage': '500 mg',
          'form': 'Tablet',
          'category': 'Analjezik',
        },
      });

      expect(result.isMatched, isTrue);
      expect(result.medicineName, 'Parol 500 mg');
      expect(result.activeIngredient, 'Parasetamol');
      expect(result.dosage, '500 mg');
    });

    test('fromJson handles not_found status', () {
      final result = MedicineBoxResult.fromJson({
        'box_index': 1,
        'yolo_confidence': 0.75,
        'matching_score': 42.0,
        'status': 'not_found',
        'display_message': 'Eslesme bulunamadi.',
        'best_candidate': 'Unknown Drug',
      });

      expect(result.isMatched, isFalse);
      expect(result.bestCandidate, 'Unknown Drug');
    });
  });

  group('AnalyzeResponse', () {
    test('fromJson parses full API payload', () {
      final response = AnalyzeResponse.fromJson({
        'success': true,
        'filename': 'sample.jpg',
        'detection_count': 1,
        'medicines_compared': 120,
        'ocr_mode': 'fast',
        'processing_time_ms': 3456.7,
        'summary': {
          'matched_count': 1,
          'not_found_count': 0,
          'not_medicine_box_count': 0,
          'error_count': 0,
        },
        'medicines': [
          {
            'box_index': 0,
            'yolo_confidence': 0.88,
            'matching_score': 92.3,
            'status': 'matched',
            'display_message': 'Parol 500 mg eslesti.',
            'medicine_name': 'Parol 500 mg',
            'medicine': {
              'active_ingredient': 'Parasetamol',
            },
          },
        ],
      });

      expect(response.success, isTrue);
      expect(response.detectionCount, 1);
      expect(response.medicines, hasLength(1));
      expect(response.summary.matchedCount, 1);
      expect(response.ocrMode, 'fast');
      expect(response.processingTimeMs, closeTo(3456.7, 0.01));
      expect(response.medicines.first.medicineName, 'Parol 500 mg');
    });

    test('fromJson parses disclaimer field', () {
      final response = AnalyzeResponse.fromJson({
        'success': true,
        'detection_count': 1,
        'disclaimer': 'Bu uygulama tibbi tavsiye vermez.',
        'medicines': [],
        'summary': {},
      });

      expect(response.disclaimer, 'Bu uygulama tibbi tavsiye vermez.');
    });

    test('fromJson tolerates missing optional fields', () {
      final response = AnalyzeResponse.fromJson({
        'success': false,
        'detection_count': 0,
      });

      expect(response.success, isFalse);
      expect(response.medicines, isEmpty);
      expect(response.summary.total, 0);
      expect(response.ocrMode, 'fast');
    });
  });
}
