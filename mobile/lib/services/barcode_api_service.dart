import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../config/app_config.dart';
import '../models/analyze_response.dart';
import 'analyze_api_exception.dart';

/// FastAPI barcode lookup / scan client.
class BarcodeApiService {
  BarcodeApiService({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConfig.apiBaseUrl;

  final http.Client _client;
  final String _baseUrl;

  Uri get _lookupUri =>
      Uri.parse('$_baseUrl${AppConfig.barcodeLookupEndpoint}');

  Uri get _scanUri => Uri.parse('$_baseUrl${AppConfig.barcodeScanEndpoint}');

  Future<AnalyzeResponse> lookupCode(String code) async {
    final uri = _lookupUri.replace(
      queryParameters: {'code': _prepareLookupCode(code)},
    );
    http.Response response;
    try {
      response = await _client.get(uri).timeout(AppConfig.barcodeTimeout);
    } on TimeoutException {
      throw AnalyzeApiException(
        'Barkod araması zaman aşımına uğradı.\n'
        'API: $_baseUrl\n'
        'Emülatörde backend açık olmalı. Telefonda APK, '
        'PC IP ile derlenmeli (10.0.2.2 yalnız emülatördür).',
      );
    } on SocketException {
      throw AnalyzeApiException(
        'Sunucuya bağlanılamadı. Backend çalışıyor mu?\n'
        'Beklenen adres: $_baseUrl',
      );
    } on http.ClientException {
      throw AnalyzeApiException(
        'Sunucuya bağlanılamadı. Backend çalışıyor mu?\n'
        'Beklenen adres: $_baseUrl',
      );
    }

    final jsonBody = _decodeJson(response.body);
    if (response.statusCode >= 400) {
      throw AnalyzeApiException(
        _errorMessage(jsonBody, response.statusCode),
        statusCode: response.statusCode,
      );
    }
    if (jsonBody == null) {
      throw AnalyzeApiException('Geçersiz sunucu yanıtı alındı.');
    }
    return _fromLookupJson(jsonBody);
  }

  Future<AnalyzeResponse> scanImage({required String imagePath}) async {
    final file = File(imagePath);
    if (!await file.exists()) {
      throw AnalyzeApiException('Seçilen dosya bulunamadı.');
    }

    final request = http.MultipartRequest('POST', _scanUri)
      ..files.add(
        await http.MultipartFile.fromPath(
          'file',
          imagePath,
          filename: _uploadFilename(imagePath),
          contentType: _contentTypeForFilename(_uploadFilename(imagePath)),
        ),
      );

    http.Response response;
    try {
      final streamed = await request.send().timeout(AppConfig.barcodeTimeout);
      response = await http.Response.fromStream(streamed)
          .timeout(AppConfig.barcodeTimeout);
    } on TimeoutException {
      throw AnalyzeApiException(
        'Barkod okuma zaman aşımına uğradı.\n'
        'API: $_baseUrl',
      );
    } on SocketException {
      throw AnalyzeApiException(
        'Sunucuya bağlanılamadı. Backend çalışıyor mu?\n'
        'Beklenen adres: $_baseUrl',
      );
    } on http.ClientException {
      throw AnalyzeApiException(
        'Sunucuya bağlanılamadı. Backend çalışıyor mu?\n'
        'Beklenen adres: $_baseUrl',
      );
    }

    final jsonBody = _decodeJson(response.body);
    if (response.statusCode >= 400) {
      throw AnalyzeApiException(
        _errorMessage(jsonBody, response.statusCode),
        statusCode: response.statusCode,
      );
    }
    if (jsonBody == null) {
      throw AnalyzeApiException('Geçersiz sunucu yanıtı alındı.');
    }
    return _fromScanJson(jsonBody);
  }

  void dispose() {
    _client.close();
  }

  AnalyzeResponse _fromLookupJson(Map<String, dynamic> json) {
    final status = json['status'] as String? ?? 'not_found';
    if (status != 'matched') {
      final barcode = json['barcode'] as String?;
      final message =
          json['display_message'] as String? ?? 'Barkod katalogda bulunamadı.';
      if (barcode != null && barcode.isNotEmpty) {
        throw AnalyzeApiException('$message\nKod: $barcode');
      }
      throw AnalyzeApiException(message);
    }
    return AnalyzeResponse.fromBarcodeMatch(
      medicine: _medicineMap(json['medicine']),
      barcode: json['barcode'] as String? ?? '',
      displayMessage:
          json['display_message'] as String? ?? 'İlaç barkod ile eşleştirildi.',
    );
  }

  AnalyzeResponse _fromScanJson(Map<String, dynamic> json) {
    final status = json['status'] as String? ?? 'no_barcode';
    if (status != 'matched') {
      final barcode = json['barcode'] as String?;
      final fallback = status == 'no_barcode'
          ? 'Görüntüde barkod okunamadı.'
          : 'Barkod katalogda bulunamadı.';
      final message = json['display_message'] as String? ?? fallback;
      if (barcode != null && barcode.isNotEmpty) {
        throw AnalyzeApiException('$message\nKod: $barcode');
      }
      throw AnalyzeApiException(message);
    }
    return AnalyzeResponse.fromBarcodeMatch(
      medicine: _medicineMap(json['medicine']),
      barcode: json['barcode'] as String? ?? '',
      displayMessage:
          json['display_message'] as String? ?? 'İlaç barkod ile eşleştirildi.',
      processingTimeMs:
          (json['processing_time_ms'] as num?)?.toDouble() ?? 0,
      disclaimer: json['disclaimer'] as String?,
    );
  }

  Map<String, String> _medicineMap(Object? raw) {
    if (raw is! Map) {
      throw AnalyzeApiException('İlaç kaydı eksik.');
    }
    return raw.map(
      (key, value) => MapEntry(key.toString(), value?.toString() ?? ''),
    );
  }

  Map<String, dynamic>? _decodeJson(String body) {
    if (body.isEmpty) {
      return null;
    }
    try {
      final decoded = jsonDecode(body);
      if (decoded is Map<String, dynamic>) {
        return decoded;
      }
    } catch (_) {
      return null;
    }
    return null;
  }

  String _errorMessage(Map<String, dynamic>? jsonBody, int statusCode) {
    final detail = jsonBody?['error'] ?? jsonBody?['detail'];
    if (detail is String && detail.isNotEmpty) {
      return detail;
    }
    return 'Sunucu hatası ($statusCode).';
  }

  String _uploadFilename(String path) {
    final parts = path.split(Platform.pathSeparator);
    final base = parts.isEmpty ? 'upload.jpg' : parts.last;
    if (base.contains('.')) {
      return base;
    }
    return '$base.jpg';
  }

  MediaType _contentTypeForFilename(String filename) {
    final lower = filename.toLowerCase();
    if (lower.endsWith('.png')) {
      return MediaType('image', 'png');
    }
    return MediaType('image', 'jpeg');
  }

  String _prepareLookupCode(String code) {
    var text = code.trim();
    final aim = RegExp(r'^\][A-Za-z]\d');
    if (aim.hasMatch(text) && text.length > 3) {
      text = text.substring(3);
    }
    return text;
  }
}
