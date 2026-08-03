import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../config/app_config.dart';
import '../models/analyze_response.dart';
import 'analyze_api_exception.dart';

/// FastAPI analyze endpoint client (multipart upload).
class AnalyzeApiService {
  AnalyzeApiService({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConfig.apiBaseUrl;

  final http.Client _client;
  final String _baseUrl;

  Uri get _analyzeUri => Uri.parse('$_baseUrl${AppConfig.analyzeEndpoint}');

  Uri get _healthUri => Uri.parse('$_baseUrl${AppConfig.healthEndpoint}');

  Future<bool> isBackendHealthy() async {
    try {
      final response = await _client
          .get(_healthUri)
          .timeout(AppConfig.healthTimeout);
      if (response.statusCode != 200) {
        return false;
      }
      final json = jsonDecode(response.body);
      if (json is! Map<String, dynamic>) {
        return false;
      }
      return json['status'] == 'ok' && json['models_loaded'] == true;
    } catch (_) {
      return false;
    }
  }

  Future<AnalyzeResponse> analyzeImage({
    required String imagePath,
    String ocrMode = 'fast',
  }) async {
    final file = File(imagePath);
    if (!await file.exists()) {
      throw AnalyzeApiException('Secilen dosya bulunamadi.');
    }

    final uri = _analyzeUri.replace(queryParameters: {'mode': ocrMode});
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await _buildMultipartFile(imagePath));

    http.StreamedResponse streamedResponse;
    http.Response response;
    try {
      streamedResponse = await request.send().timeout(AppConfig.analyzeTimeout);
      response = await http.Response.fromStream(streamedResponse)
          .timeout(AppConfig.analyzeTimeout);
    } on TimeoutException {
      throw AnalyzeApiException(
        'Analiz zaman asimina ugradi (${AppConfig.analyzeTimeout.inSeconds} sn). '
        'CPU uzerinde OCR uzun surebilir; tekrar deneyin ve analiz bitene kadar bekleyin.',
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

    if (response.statusCode == 413) {
      throw AnalyzeApiException(
        'Dosya cok buyuk. Daha kucuk bir fotograf secin.',
        statusCode: response.statusCode,
      );
    }

    Map<String, dynamic>? jsonBody;
    if (body.isNotEmpty) {
      try {
        final decoded = jsonDecode(body);
        if (decoded is Map<String, dynamic>) {
          jsonBody = decoded;
        }
      } catch (_) {
        // fall through to generic error below
      }
    }

    if (response.statusCode >= 400) {
      final detail = jsonBody?['error'] ?? jsonBody?['detail'];
      final message = detail is String
          ? detail
          : 'Sunucu hatasi (${response.statusCode}).';
      throw AnalyzeApiException(message, statusCode: response.statusCode);
    }

    if (jsonBody == null) {
      throw AnalyzeApiException('Gecersiz sunucu yaniti alindi.');
    }

    return AnalyzeResponse.fromJson(jsonBody);
  }

  void dispose() {
    _client.close();
  }

  String _basename(String path) {
    final parts = path.split(Platform.pathSeparator);
    return parts.isEmpty ? 'upload.jpg' : parts.last;
  }

  Future<http.MultipartFile> _buildMultipartFile(String imagePath) async {
    final filename = _uploadFilename(imagePath);
    return http.MultipartFile.fromPath(
      'file',
      imagePath,
      filename: filename,
      contentType: _contentTypeForFilename(filename),
    );
  }

  /// Android galeri yollari bazen uzantisiz gelir; backend icin .jpg eklenir.
  String _uploadFilename(String path) {
    final base = _basename(path);
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
    if (lower.endsWith('.webp')) {
      return MediaType('image', 'webp');
    }
    if (lower.endsWith('.bmp')) {
      return MediaType('image', 'bmp');
    }
    return MediaType('image', 'jpeg');
  }
}
