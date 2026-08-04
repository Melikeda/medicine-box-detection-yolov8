import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../models/explain_response.dart';
import 'analyze_api_exception.dart';

/// FastAPI explain endpoint client.
class ExplainApiService {
  ExplainApiService({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConfig.apiBaseUrl;

  final http.Client _client;
  final String _baseUrl;

  Uri get _explainUri => Uri.parse('$_baseUrl${AppConfig.explainEndpoint}');

  Future<ExplainResponse> fetchExplanation({
    required String medicineId,
    String locale = 'tr',
  }) async {
    final request = http.Request('POST', _explainUri)
      ..headers['Content-Type'] = 'application/json; charset=utf-8'
      ..body = jsonEncode({
        'medicine_id': medicineId,
        'locale': locale,
      });

    http.StreamedResponse streamedResponse;
    http.Response response;
    try {
      streamedResponse = await _client
          .send(request)
          .timeout(AppConfig.explainTimeout);
      response = await http.Response.fromStream(streamedResponse)
          .timeout(AppConfig.explainTimeout);
    } on TimeoutException {
      throw AnalyzeApiException(
        'Aciklama istegi zaman asimina ugradi. Tekrar deneyin.',
      );
    } on SocketException {
      throw AnalyzeApiException(
        'Sunucuya baglanilamadi. Backend calisiyor mu?\n'
        'Beklenen adres: $_baseUrl',
      );
    } on HttpException {
      throw AnalyzeApiException('Ag hatasi olustu. Baglantinizi kontrol edin.');
    }

    final body = response.body;
    Map<String, dynamic>? jsonBody;
    if (body.isNotEmpty) {
      try {
        final decoded = jsonDecode(body);
        if (decoded is Map<String, dynamic>) {
          jsonBody = decoded;
        }
      } catch (_) {
        // fall through
      }
    }

    if (response.statusCode >= 400) {
      final detail = jsonBody?['error'] ?? jsonBody?['detail'];
      final message = detail is String
          ? detail
          : 'Aciklama alinamadi (${response.statusCode}).';
      throw AnalyzeApiException(message, statusCode: response.statusCode);
    }

    if (jsonBody == null) {
      throw AnalyzeApiException('Gecersiz sunucu yaniti alindi.');
    }

    return ExplainResponse.fromJson(jsonBody);
  }

  void dispose() {
    _client.close();
  }
}
