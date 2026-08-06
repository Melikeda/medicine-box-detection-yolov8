import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';

import '../routes/app_router.dart';
import '../services/analyze_api_exception.dart';
import '../services/analyze_api_service.dart';
import '../services/scan_history_service.dart';
import '../theme/app_colors.dart';
import '../widgets/loading_overlay.dart';

class ImagePreviewScreen extends StatefulWidget {
  const ImagePreviewScreen({
    super.key,
    required this.imagePath,
    this.analyzeService,
    this.historyService,
  });

  final String imagePath;
  final AnalyzeApiService? analyzeService;
  final ScanHistoryService? historyService;

  @override
  State<ImagePreviewScreen> createState() => _ImagePreviewScreenState();
}

class _ImagePreviewScreenState extends State<ImagePreviewScreen> {
  late final AnalyzeApiService _analyzeService;
  late final ScanHistoryService _historyService;
  bool _isAnalyzing = false;

  @override
  void initState() {
    super.initState();
    _analyzeService = widget.analyzeService ?? AnalyzeApiService();
    _historyService = widget.historyService ?? ScanHistoryService();
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

      unawaited(
        _historyService.saveScan(
          response: response,
          imagePath: widget.imagePath,
        ),
      );

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
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          onPressed: _isAnalyzing ? null : () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.primary.withValues(alpha: 0.06),
                            blurRadius: 20,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(24),
                        child: Image.file(
                          file,
                          fit: BoxFit.contain,
                          width: double.infinity,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.cameraCard,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.auto_awesome_outlined,
                          color: AppColors.cameraIcon,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'Analiz, YOLO tespiti ve OCR ile ilac '
                            'kutularini tanir.',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: AppColors.primary,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: _isAnalyzing ? null : _analyze,
                    icon: _isAnalyzing
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Icon(Icons.search_rounded),
                    label: Text(
                      _isAnalyzing ? 'Analiz ediliyor...' : 'Analiz Et',
                    ),
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton.icon(
                    onPressed: _isAnalyzing
                        ? null
                        : () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.refresh_rounded),
                    label: const Text('Baska fotograf sec'),
                  ),
                ],
              ),
            ),
            if (_isAnalyzing)
              const LoadingOverlay(
                message: 'Ilac kutusu analiz ediliyor...',
                subtitle:
                    'CPU uzerinde OCR 1-3 dakika surebilir (fast mod).',
              ),
          ],
        ),
      ),
    );
  }
}
