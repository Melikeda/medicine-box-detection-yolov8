import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../models/analyze_response.dart';
import 'analyze_api_exception.dart';

/// FastAPI server scan-history client (`POST /api/v1/scans`).
///
/// Best-effort sync: local history remains source of truth for the UI.
class ScanApiService {
  ScanApiService({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConfig.apiBaseUrl;

  final http.Client _client;
  final String _baseUrl;

  Uri get _scansUri => Uri.parse('$_baseUrl${AppConfig.scansEndpoint}');

  /// Uploads a successful analyze payload. Returns server scan id when ok.
  Future<int?> createScan({
    required AnalyzeResponse response,
    String? previewLabel,
    String? clientDeviceId,
  }) async {
    if (!response.success) {
      return null;
    }

    final body = <String, dynamic>{
      'response': response.toJson(),
      if (previewLabel != null && previewLabel.isNotEmpty)
        'preview_label': previewLabel,
      if (clientDeviceId != null && clientDeviceId.isNotEmpty)
        'client_device_id': clientDeviceId,
    };

    http.Response httpResponse;
    try {
      httpResponse = await _client
          .post(
            _scansUri,
            headers: const {
              'Content-Type': 'application/json; charset=utf-8',
            },
            body: jsonEncode(body),
          )
          .timeout(AppConfig.scansTimeout);
    } on TimeoutException {
      throw AnalyzeApiException(
        'Sunucu gecmisi senkronu zaman asimina ugradi.',
      );
    } on SocketException {
      throw AnalyzeApiException(
        'Sunucu gecmisi senkronu icin baglanti kurulamadi.',
      );
    } on HttpException {
      throw AnalyzeApiException('Sunucu gecmisi senkronunda ag hatasi.');
    }

    if (httpResponse.statusCode >= 400) {
      String message =
          'Sunucu gecmisi kaydedilemedi (${httpResponse.statusCode}).';
      try {
        final decoded = jsonDecode(httpResponse.body);
        if (decoded is Map<String, dynamic>) {
          final detail = decoded['error'] ?? decoded['detail'];
          if (detail is String && detail.isNotEmpty) {
            message = detail;
          }
        }
      } catch (_) {
        // keep default
      }
      throw AnalyzeApiException(
        message,
        statusCode: httpResponse.statusCode,
      );
    }

    try {
      final decoded = jsonDecode(httpResponse.body);
      if (decoded is Map<String, dynamic>) {
        final scan = decoded['scan'];
        if (scan is Map<String, dynamic>) {
          final id = scan['id'];
          if (id is int) {
            return id;
          }
        }
      }
    } catch (_) {
      // ignore parse issues — upload itself succeeded
    }
    return null;
  }

  void dispose() {
    _client.close();
  }
}
