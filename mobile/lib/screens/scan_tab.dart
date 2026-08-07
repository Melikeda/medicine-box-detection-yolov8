import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../l10n/app_localizations.dart';
import '../theme/app_colors.dart';
import '../widgets/animated_pastel_background.dart';
import '../widgets/capsule_background.dart';
import '../widgets/language_toggle.dart';

enum PickSource { camera, gallery }

/// Kamera / galeri tarama sayfasi.
class ScanTab extends StatelessWidget {
  const ScanTab({
    super.key,
    required this.onCameraTap,
    required this.onGalleryTap,
    this.isPicking = false,
    this.activePickSource,
  });

  final VoidCallback onCameraTap;
  final VoidCallback onGalleryTap;
  final bool isPicking;
  final PickSource? activePickSource;

  bool _isLoading(PickSource source) {
    return isPicking && activePickSource == source;
  }

  @override
  Widget build(BuildContext context) {
    final s = context.s;

    return AnimatedPastelBackground(
      child: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Align(
                alignment: Alignment.centerRight,
                child: LanguageToggle(),
              ),
              const SizedBox(height: 6),
              Text(
                s.scanTitle,
                style: GoogleFonts.poppins(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                s.scanSubtitle,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 18),
              _ScanViewfinder(
                label: s.alignBox,
                tryLabel: s.tryCamera,
                tryHint: s.tryCameraHint,
                isLoading: _isLoading(PickSource.camera),
                onTryCamera: onCameraTap,
              ),
              const SizedBox(height: 16),
              _GalleryActionCard(
                title: s.pickGallery,
                subtitle: s.pickGalleryHint,
                isLoading: _isLoading(PickSource.gallery),
                onTap: onGalleryTap,
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ),
    );
  }
}

class _ScanViewfinder extends StatefulWidget {
  const _ScanViewfinder({
    required this.label,
    required this.tryLabel,
    required this.tryHint,
    required this.onTryCamera,
    this.isLoading = false,
  });

  final String label;
  final String tryLabel;
  final String tryHint;
  final VoidCallback onTryCamera;
  final bool isLoading;

  @override
  State<_ScanViewfinder> createState() => _ScanViewfinderState();
}

class _ScanViewfinderState extends State<_ScanViewfinder>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: widget.isLoading ? null : widget.onTryCamera,
        borderRadius: BorderRadius.circular(24),
        child: Ink(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Color(0xFF0F172A),
                Color(0xFF1E293B),
                Color(0xFF0B1220),
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.accent.withValues(alpha: 0.18),
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 18, 16, 14),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 150,
                    height: 150,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        CustomPaint(
                          size: const Size(112, 112),
                          painter: _RealisticQrPainter(),
                        ),
                        CustomPaint(
                          size: const Size(148, 148),
                          painter: _CornerBracketPainter(
                            color: AppColors.accentLight,
                          ),
                        ),
                        AnimatedBuilder(
                          animation: _controller,
                          builder: (context, _) {
                            return Align(
                              alignment: Alignment(
                                0,
                                -0.82 + _controller.value * 1.64,
                              ),
                              child: Container(
                                width: 116,
                                height: 2,
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    colors: [
                                      Colors.transparent,
                                      AppColors.accentLight
                                          .withValues(alpha: 0.95),
                                      Colors.transparent,
                                    ],
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: AppColors.accentLight
                                          .withValues(alpha: 0.55),
                                      blurRadius: 8,
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    widget.label,
                    textAlign: TextAlign.center,
                    style: GoogleFonts.poppins(
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 10,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: Colors.white.withValues(alpha: 0.18),
                      ),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 34,
                          height: 34,
                          decoration: BoxDecoration(
                            color: AppColors.teal.withValues(alpha: 0.45),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: widget.isLoading
                              ? const Padding(
                                  padding: EdgeInsets.all(8),
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Colors.white,
                                  ),
                                )
                              : const Icon(
                                  Icons.center_focus_strong_rounded,
                                  size: 20,
                                  color: AppColors.accentLight,
                                ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                widget.tryLabel,
                                style: GoogleFonts.poppins(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: Colors.white,
                                ),
                              ),
                              Text(
                                widget.tryHint,
                                style: GoogleFonts.poppins(
                                  fontSize: 11,
                                  color: Colors.white.withValues(alpha: 0.75),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Icon(
                          Icons.chevron_right_rounded,
                          color: Colors.white70,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _CornerBracketPainter extends CustomPainter {
  _CornerBracketPainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 3.2
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    const len = 22.0;
    final rect = Rect.fromLTWH(0, 0, size.width, size.height);

    // TL
    canvas.drawLine(rect.topLeft, rect.topLeft + const Offset(len, 0), paint);
    canvas.drawLine(rect.topLeft, rect.topLeft + const Offset(0, len), paint);
    // TR
    canvas.drawLine(rect.topRight, rect.topRight + const Offset(-len, 0), paint);
    canvas.drawLine(rect.topRight, rect.topRight + const Offset(0, len), paint);
    // BL
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
    // BR
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
  bool shouldRepaint(covariant _CornerBracketPainter oldDelegate) =>
      oldDelegate.color != color;
}

/// Gercekci gorunumlu QR modul deseni.
class _RealisticQrPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final bg = Paint()..color = Colors.white;
    final ink = Paint()..color = const Color(0xFF0F172A);
    final rrect = RRect.fromRectAndRadius(
      Offset.zero & size,
      const Radius.circular(10),
    );
    canvas.drawRRect(rrect, bg);

    const modules = 21;
    final cell = size.width / modules;
    final rng = math.Random(17);

    bool isFinder(int x, int y) {
      bool inCorner(int ox, int oy) =>
          x >= ox && x < ox + 7 && y >= oy && y < oy + 7;
      return inCorner(0, 0) || inCorner(modules - 7, 0) || inCorner(0, modules - 7);
    }

    void drawFinder(int ox, int oy) {
      canvas.drawRect(
        Rect.fromLTWH(ox * cell, oy * cell, 7 * cell, 7 * cell),
        ink,
      );
      canvas.drawRect(
        Rect.fromLTWH((ox + 1) * cell, (oy + 1) * cell, 5 * cell, 5 * cell),
        bg,
      );
      canvas.drawRect(
        Rect.fromLTWH((ox + 2) * cell, (oy + 2) * cell, 3 * cell, 3 * cell),
        ink,
      );
    }

    for (var y = 0; y < modules; y++) {
      for (var x = 0; x < modules; x++) {
        if (isFinder(x, y)) {
          continue;
        }
        if (rng.nextBool()) {
          canvas.drawRect(
            Rect.fromLTWH(x * cell, y * cell, cell * 0.92, cell * 0.92),
            ink,
          );
        }
      }
    }

    drawFinder(0, 0);
    drawFinder(modules - 7, 0);
    drawFinder(0, modules - 7);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _GalleryActionCard extends StatelessWidget {
  const _GalleryActionCard({
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.isLoading = false,
  });

  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: isLoading ? null : onTap,
        borderRadius: BorderRadius.circular(24),
        child: Ink(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                AppColors.pastelGreen,
                AppColors.pastelAqua,
                Color(0xFF95D5B2),
              ],
            ),
            border: Border.all(color: AppColors.medicineSage),
            boxShadow: [
              BoxShadow(
                color: AppColors.galleryIcon.withValues(alpha: 0.16),
                blurRadius: 14,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
            child: Row(
              children: [
                isLoading
                    ? const SizedBox(
                        width: 74,
                        height: 74,
                        child: Center(
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                      )
                    : const _GalleryThumbGrid(),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: GoogleFonts.poppins(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primary,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: GoogleFonts.poppins(
                          fontSize: 12.5,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.chevron_right_rounded,
                  color: AppColors.darkGreen.withValues(alpha: 0.55),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _GalleryThumbGrid extends StatelessWidget {
  const _GalleryThumbGrid();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 74,
      height: 74,
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.8),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white),
        boxShadow: [
          BoxShadow(
            color: AppColors.medicineGreen.withValues(alpha: 0.12),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Mini medicine box silhouette
          Align(
            alignment: const Alignment(-0.15, 0.1),
            child: Transform.rotate(
              angle: -0.12,
              child: Container(
                width: 34,
                height: 44,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(4),
                  gradient: const LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Color(0xFFFFFFFF),
                      Color(0xFFE8F5EE),
                      Color(0xFFD5E8DB),
                    ],
                  ),
                  border: Border.all(color: const Color(0xFFA7C4B0)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.1),
                      blurRadius: 4,
                      offset: const Offset(1, 2),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Container(
                      height: 7,
                      decoration: const BoxDecoration(
                        color: Color(0xFF2D6A4F),
                        borderRadius: BorderRadius.vertical(
                          top: Radius.circular(3),
                        ),
                      ),
                    ),
                    const Spacer(),
                    Text(
                      'Rx',
                      style: GoogleFonts.poppins(
                        fontSize: 9,
                        fontWeight: FontWeight.w700,
                        color: const Color(0xFF2D6A4F),
                      ),
                    ),
                    const Spacer(),
                  ],
                ),
              ),
            ),
          ),
          // Soft capsule overlapping the box
          Align(
            alignment: const Alignment(0.75, -0.35),
            child: Transform.rotate(
              angle: 0.55,
              child: const RealisticCapsule(
                width: 36,
                height: 14,
                leftColor: Color(0xFF3A9FBF),
                rightColor: Color(0xFFE8DFCF),
                opacity: 0.95,
              ),
            ),
          ),
          Align(
            alignment: const Alignment(0.55, 0.7),
            child: Transform.rotate(
              angle: -0.35,
              child: const RealisticCapsule(
                width: 28,
                height: 11,
                leftColor: Color(0xFFD4A820),
                rightColor: Color(0xFFF2D98A),
                opacity: 0.92,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
