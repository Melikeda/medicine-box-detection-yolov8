import 'dart:async';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../config/app_config.dart';
import '../l10n/app_localizations.dart';
import '../models/analyze_response.dart';
import '../routes/app_router.dart';
import '../services/analyze_api_exception.dart';
import '../services/barcode_api_service.dart';
import '../services/image_picker_service.dart';
import '../services/scan_api_service.dart';
import '../services/scan_history_service.dart';
import '../theme/app_colors.dart';
import '../widgets/loading_overlay.dart';

/// Canlı barkod kadrajı + fotoğraftan okuma yedeği.
class BarcodeScannerScreen extends StatefulWidget {
  const BarcodeScannerScreen({
    super.key,
    this.apiService,
    this.historyService,
    this.scanApiService,
    this.imagePicker,
  });

  final BarcodeApiService? apiService;
  final ScanHistoryService? historyService;
  final ScanApiService? scanApiService;
  final ImagePickerService? imagePicker;

  @override
  State<BarcodeScannerScreen> createState() => _BarcodeScannerScreenState();
}

class _BarcodeScannerScreenState extends State<BarcodeScannerScreen> {
  late final BarcodeApiService _apiService;
  late final ScanHistoryService _historyService;
  late final ScanApiService _scanApiService;
  late final ImagePickerService _imagePicker;
  late final MobileScannerController _controller;

  bool _busy = false;
  bool _handledCode = false;

  @override
  void initState() {
    super.initState();
    _apiService = widget.apiService ?? BarcodeApiService();
    _historyService = widget.historyService ?? ScanHistoryService();
    _scanApiService = widget.scanApiService ?? ScanApiService();
    _imagePicker = widget.imagePicker ?? ImagePickerService();
    _controller = MobileScannerController(
      detectionSpeed: DetectionSpeed.normal,
      facing: CameraFacing.back,
      formats: const [
        BarcodeFormat.ean13,
        BarcodeFormat.ean8,
        BarcodeFormat.upcA,
        BarcodeFormat.upcE,
        BarcodeFormat.code128,
        BarcodeFormat.qrCode,
        BarcodeFormat.dataMatrix,
      ],
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    if (widget.apiService == null) {
      _apiService.dispose();
    }
    if (widget.scanApiService == null) {
      _scanApiService.dispose();
    }
    super.dispose();
  }

  Future<void> _onDetect(BarcodeCapture capture) async {
    if (_busy || _handledCode) {
      return;
    }
    final code = capture.barcodes
        .map((item) => item.rawValue)
        .whereType<String>()
        .map((value) => value.trim())
        .firstWhere(
          (value) => value.length >= 8,
          orElse: () => '',
        );
    if (code.isEmpty) {
      return;
    }
    await _lookupAndShow(code);
  }

  Future<void> _lookupAndShow(String code) async {
    if (_busy) {
      return;
    }
    setState(() {
      _busy = true;
      _handledCode = true;
    });
    await _controller.stop();

    try {
      final response = await _apiService.lookupCode(code);
      if (!mounted) {
        return;
      }
      await _openResult(response);
    } on AnalyzeApiException catch (error) {
      if (!mounted) {
        return;
      }
      _showError(error.message);
      await _resumeScanner();
    } catch (error) {
      if (!mounted) {
        return;
      }
      _showError(context.s.unexpectedErrorWith(error));
      await _resumeScanner();
    }
  }

  Future<void> _scanFromPhoto() async {
    if (_busy) {
      return;
    }
    setState(() => _busy = true);
    await _controller.stop();

    try {
      final path = await _imagePicker.pickFromGallery();
      if (!mounted) {
        return;
      }
      if (path == null) {
        await _resumeScanner();
        return;
      }
      final response = await _apiService.scanImage(imagePath: path);
      if (!mounted) {
        return;
      }
      await _openResult(response, imagePath: path);
    } on AnalyzeApiException catch (error) {
      if (!mounted) {
        return;
      }
      _showError(error.message);
      await _resumeScanner();
    } catch (error) {
      if (!mounted) {
        return;
      }
      _showError(context.s.unexpectedErrorWith(error));
      await _resumeScanner();
    }
  }

  Future<void> _openResult(
    AnalyzeResponse response, {
    String? imagePath,
  }) async {
    unawaited(_persistScanHistory(response, imagePath: imagePath));
    await Navigator.of(context).pushNamed(
      AppRoutes.result,
      arguments: ResultRouteArgs(
        response: response,
        imagePath: imagePath,
      ),
    );
    if (mounted) {
      await _resumeScanner();
    }
  }

  Future<void> _persistScanHistory(
    AnalyzeResponse response, {
    String? imagePath,
  }) async {
    await _historyService.saveScan(
      response: response,
      imagePath: imagePath,
    );
    try {
      await _scanApiService.createScan(response: response);
    } catch (_) {
      // Offline / server down — local history still available.
    }
  }

  Future<void> _resumeScanner() async {
    _handledCode = false;
    if (!mounted) {
      return;
    }
    setState(() => _busy = false);
    try {
      await _controller.start();
    } catch (_) {
      // Permission / camera already running.
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = context.s;

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        title: Text(s.scanBarcode),
      ),
      body: Stack(
        fit: StackFit.expand,
        children: [
          MobileScanner(
            controller: _controller,
            onDetect: _onDetect,
          ),
          const _BarcodeFrameOverlay(),
          Align(
            alignment: Alignment.topCenter,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
                child: Text(
                  s.barcodeAlign,
                  textAlign: TextAlign.center,
                  style: GoogleFonts.poppins(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                    fontSize: 15,
                    shadows: const [
                      Shadow(color: Colors.black54, blurRadius: 8),
                    ],
                  ),
                ),
              ),
            ),
          ),
          Align(
            alignment: Alignment.bottomCenter,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      s.scanBarcodeHint,
                      textAlign: TextAlign.center,
                      style: GoogleFonts.poppins(
                        color: Colors.white70,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      AppConfig.apiBaseUrl,
                      textAlign: TextAlign.center,
                      style: GoogleFonts.poppins(
                        color: Colors.white38,
                        fontSize: 11,
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: _busy ? null : _scanFromPhoto,
                        icon: const Icon(Icons.photo_library_outlined),
                        label: Text(s.barcodeFromPhoto),
                        style: FilledButton.styleFrom(
                          backgroundColor: AppColors.teal,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          if (_busy)
            LoadingOverlay(
              message: s.barcodeLookingUp,
              subtitle: s.scanBarcodeHint,
            ),
        ],
      ),
    );
  }
}

class _BarcodeFrameOverlay extends StatelessWidget {
  const _BarcodeFrameOverlay();

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Center(
        child: SizedBox(
          width: 240,
          height: 160,
          child: CustomPaint(
            painter: _BarcodeBracketPainter(color: AppColors.accentLight),
          ),
        ),
      ),
    );
  }
}

class _BarcodeBracketPainter extends CustomPainter {
  _BarcodeBracketPainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    const len = 28.0;
    final rect = Offset.zero & size;
    canvas.drawLine(rect.topLeft, rect.topLeft + const Offset(len, 0), paint);
    canvas.drawLine(rect.topLeft, rect.topLeft + const Offset(0, len), paint);
    canvas.drawLine(rect.topRight, rect.topRight + const Offset(-len, 0), paint);
    canvas.drawLine(rect.topRight, rect.topRight + const Offset(0, len), paint);
    canvas.drawLine(
      rect.bottomLeft,
      rect.bottomLeft + const Offset(len, 0),
      paint,
    );
    canvas.drawLine(
      rect.bottomLeft,
      rect.bottomLeft + const Offset(0, -len),
      paint,
    );
    canvas.drawLine(
      rect.bottomRight,
      rect.bottomRight + const Offset(-len, 0),
      paint,
    );
    canvas.drawLine(
      rect.bottomRight,
      rect.bottomRight + const Offset(0, -len),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant _BarcodeBracketPainter oldDelegate) =>
      oldDelegate.color != color;
}
