import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:yolocilin/models/analyze_response.dart';
import 'package:yolocilin/services/analyze_api_exception.dart';
import 'package:yolocilin/services/barcode_api_service.dart';

void main() {
  test('lookupCode maps matched medicine to AnalyzeResponse', () async {
    final client = MockClient((request) async {
      expect(request.url.path, '/api/v1/barcode/lookup');
      expect(request.url.queryParameters['code'], '8699522090471');
      return http.Response(
        '{"success":true,"status":"matched","barcode":"8699522090471",'
        '"display_message":"Ilac barkod ile eslestirildi.",'
        '"medicine":{"medicine_id":"MED001","medicine_name":"Parol",'
        '"brand_name":"Parol","active_ingredient":"Paracetamol",'
        '"dosage":"500 mg","form":"Tablet","category":"Agri Kesici"}}',
        200,
        headers: {'content-type': 'application/json'},
      );
    });

    final service = BarcodeApiService(
      client: client,
      baseUrl: 'http://example.test',
    );
    final response = await service.lookupCode('8699522090471');
    expect(response.success, isTrue);
    expect(response.ocrMode, 'barcode');
    expect(response.medicines, hasLength(1));
    expect(response.medicines.first.medicineName, 'Parol');
    expect(response.medicines.first.matchSource, 'barcode');
    expect(response.medicines.first.barcode, '8699522090471');
    expect(response.medicines.first.medicineId, 'MED001');
    service.dispose();
  });

  test('lookupCode throws on catalog miss', () async {
    final client = MockClient((request) async {
      return http.Response(
        '{"success":false,"status":"not_found","barcode":"000",'
        '"display_message":"Barkod katalogda bulunamadi."}',
        200,
        headers: {'content-type': 'application/json'},
      );
    });
    final service = BarcodeApiService(
      client: client,
      baseUrl: 'http://example.test',
    );
    expect(
      () => service.lookupCode('0000000000000'),
      throwsA(isA<AnalyzeApiException>()),
    );
    service.dispose();
  });

  test('lookupCode strips AIM ]C1 prefix before requesting', () async {
    final client = MockClient((request) async {
      expect(request.url.queryParameters['code'], '8699832090055');
      return http.Response(
        '{"success":true,"status":"matched","barcode":"8699832090055",'
        '"display_message":"ok",'
        '"medicine":{"medicine_id":"MED008","medicine_name":"Arveles"}}',
        200,
        headers: {'content-type': 'application/json'},
      );
    });
    final service = BarcodeApiService(
      client: client,
      baseUrl: 'http://example.test',
    );
    final response = await service.lookupCode(']C18699832090055');
    expect(response.medicines.first.medicineName, 'Arveles');
    service.dispose();
  });

  test('fromBarcodeMatch builds result-screen payload', () {
    final response = AnalyzeResponse.fromBarcodeMatch(
      medicine: const {
        'medicine_id': 'MED001',
        'medicine_name': 'Parol',
      },
      barcode: '8699522090471',
      displayMessage: 'matched',
    );
    expect(response.summary.matchedCount, 1);
    expect(response.medicines.first.isMatched, isTrue);
  });
}
