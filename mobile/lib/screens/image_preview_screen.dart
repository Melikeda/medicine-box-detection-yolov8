import 'dart:io';

import 'package:flutter/material.dart';

import '../routes/app_router.dart';
import '../services/analyze_api_exception.dart';
import '../services/analyze_api_service.dart';

class ImagePreviewScreen extends StatefulWidget {
  const ImagePreviewScreen({
    super.key,
    required this.imagePath,
    this.analyzeService,
  });

  final String imagePath;
  final AnalyzeApiService? analyzeService;

  @override
  State<ImagePreviewScreen> createState() => _ImagePreviewScreenState();
}

class _ImagePreviewScreenState extends State<ImagePreviewScreen> {
  late final AnalyzeApiService _analyzeService;
  bool _isAnalyzing = false;

  @override
  void initState() {
    super.initState();
    _analyzeService = widget.analyzeService ?? AnalyzeApiService();
  }

  @override
  void dispose() {
    if (widget.analyzeService == null) {
      _analyzeService.dispose();
    }
    super.dispose();
  }

  Future<void> _analyze() async {
    if (_isAnalyzing) {
      return;
    }

    setState(() => _isAnalyzing = true);

    try {
      final healthy = await _analyzeService.isBackendHealthy();
      if (!healthy) {
        if (!mounted) {
          return;
        }
        _showError(
          'Backend hazir degil veya modeller yuklenmedi.\n'
          'Once python run_api.py calistirin.',
        );
        return;
      }

      final response = await _analyzeService.analyzeImage(
        imagePath: widget.imagePath,
      );

      if (!mounted) {
        return;
      }

      await Navigator.of(context).pushNamed(
        AppRoutes.result,
        arguments: ResultRouteArgs(
          response: response,
          imagePath: widget.imagePath,
        ),
      );
    } on AnalyzeApiException catch (error) {
      if (!mounted) {
        return;
      }
      _showError(error.message);
    } catch (error) {
      if (!mounted) {
        return;
      }
      _showError('Beklenmeyen hata: $error');
    } finally {
      if (mounted) {
        setState(() => _isAnalyzing = false);
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final file = File(widget.imagePath);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Onizleme'),
      ),
      body: SafeArea(
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surfaceContainerHighest,
                        ),
                        child: Image.file(
                          file,
                          fit: BoxFit.contain,
                          width: double.infinity,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Icon(
                            Icons.cloud_upload_outlined,
                            color: theme.colorScheme.primary,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Analiz, FastAPI uzerindeki YOLO + OCR '
                              'pipeline\'ini calistirir.',
                              style: theme.textTheme.bodyMedium,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: _isAnalyzing ? null : _analyze,
                    icon: _isAnalyzing
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.search),
                    label: Text(
                      _isAnalyzing ? 'Analiz ediliyor...' : 'Analiz Et',
                    ),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: _isAnalyzing
                        ? null
                        : () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.arrow_back),
                    label: const Text('Geri Don'),
                  ),
                ],
              ),
            ),
            if (_isAnalyzing)
              ColoredBox(
                color: Colors.black.withValues(alpha: 0.25),
                child: const Center(
                  child: Card(
                    child: Padding(
                      padding: EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          CircularProgressIndicator(),
                          SizedBox(height: 16),
                          Text('Ilac kutusu analiz ediliyor...'),
                          SizedBox(height: 4),
                          Text(
                            'CPU uzerinde OCR 1-3 dakika surebilir.',
                            style: TextStyle(fontSize: 12),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
