import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_colors.dart';

/// Beyaz-yesil 3B Yolocilin ilac kutusu (arka plan kapsulleri sayfa background'unda).
class AnimatedYolocilinHero3D extends StatefulWidget {
  const AnimatedYolocilinHero3D({super.key, this.scale = 1.0});

  final double scale;

  @override
  State<AnimatedYolocilinHero3D> createState() =>
      _AnimatedYolocilinHero3DState();
}

class _AnimatedYolocilinHero3DState extends State<AnimatedYolocilinHero3D>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final s = widget.scale;
    final boxW = 128.0 * s;
    final boxH = 168.0 * s;
    final depth = boxW * 0.32;

    return SizedBox(
      width: 220 * s,
      height: 210 * s,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          final t = _controller.value * 2 * math.pi;
          final angle = math.sin(t * 0.45) * 0.22;

          return Stack(
            alignment: Alignment.center,
            clipBehavior: Clip.none,
            children: [
              Positioned(
                bottom: 18 * s,
                child: Container(
                  width: boxW * 0.85,
                  height: 14 * s,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(999),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.medicineGreenDark.withValues(
                          alpha: 0.22,
                        ),
                        blurRadius: 24 * s,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                ),
              ),
              Transform(
                alignment: Alignment.center,
                transform: Matrix4.identity()
                  ..setEntry(3, 2, 0.0015)
                  ..rotateY(angle),
                child: _MedicineBox3D(
                  width: boxW,
                  height: boxH,
                  depth: depth,
                  scale: s,
                  angle: angle,
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _MedicineBox3D extends StatelessWidget {
  const _MedicineBox3D({
    required this.width,
    required this.height,
    required this.depth,
    required this.scale,
    required this.angle,
  });

  final double width;
  final double height;
  final double depth;
  final double scale;
  final double angle;

  @override
  Widget build(BuildContext context) {
    final sideShift = math.sin(angle) * depth * 0.5;

    return SizedBox(
      width: width + depth,
      height: height + depth * 0.35,
      child: Stack(
        alignment: Alignment.center,
        clipBehavior: Clip.none,
        children: [
          if (angle >= 0)
            Transform.translate(
              offset: Offset(sideShift + depth * 0.42, 0),
              child: _SideFace(width: depth, height: height * 0.97),
            ),
          _FrontFace(width: width, height: height, scale: scale),
          if (angle < 0)
            Transform.translate(
              offset: Offset(sideShift - depth * 0.42, 0),
              child: _SideFace(width: depth, height: height * 0.97),
            ),
          Transform.translate(
            offset: Offset(0, -height * 0.5),
            child: Transform(
              alignment: Alignment.bottomCenter,
              transform: Matrix4.identity()
                ..setEntry(3, 2, 0.002)
                ..rotateX(-1.2)
                ..rotateY(angle * 0.35),
              child: _TopFace(width: width * 0.98, depth: depth),
            ),
          ),
        ],
      ),
    );
  }
}

class _FrontFace extends StatelessWidget {
  const _FrontFace({
    required this.width,
    required this.height,
    required this.scale,
  });

  final double width;
  final double height;
  final double scale;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(6 * scale),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFFFFFFF),
            Color(0xFFF3F8F4),
            Color(0xFFE7F0EA),
          ],
        ),
        border: Border.all(color: const Color(0xFFC9D9CE)),
        boxShadow: [
          BoxShadow(
            color: AppColors.medicineGreenDark.withValues(alpha: 0.2),
            blurRadius: 16 * scale,
            offset: Offset(8 * scale, 12 * scale),
          ),
        ],
      ),
      child: Stack(
        children: [
          Positioned(
            left: 0,
            top: 0,
            bottom: 0,
            width: 10 * scale,
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                  colors: [
                    AppColors.medicineGreen.withValues(alpha: 0.55),
                    AppColors.medicineGreenLight.withValues(alpha: 0.15),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            left: 0,
            right: 0,
            top: 0,
            height: 8 * scale,
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AppColors.medicineGreenDark.withValues(alpha: 0.75),
                    AppColors.medicineGreen.withValues(alpha: 0.55),
                  ],
                ),
              ),
            ),
          ),
          Center(
            child: Text(
              'Yolocilin',
              textAlign: TextAlign.center,
              style: GoogleFonts.playfairDisplay(
                fontSize: 26 * scale,
                fontWeight: FontWeight.w700,
                fontStyle: FontStyle.italic,
                color: AppColors.medicineGreenDark,
                height: 1.0,
              ),
            ),
          ),
          Positioned(
            left: width * 0.12,
            top: height * 0.12,
            child: Container(
              width: width * 0.07,
              height: height * 0.55,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(999),
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.white.withValues(alpha: 0.75),
                    Colors.white.withValues(alpha: 0.0),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SideFace extends StatelessWidget {
  const _SideFace({required this.width, required this.height});

  final double width;
  final double height;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(3),
        gradient: const LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: [
            Color(0xFF1B4332),
            Color(0xFF2D6A4F),
            Color(0xFF40916C),
          ],
        ),
      ),
    );
  }
}

class _TopFace extends StatelessWidget {
  const _TopFace({required this.width, required this.depth});

  final double width;
  final double depth;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: depth,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(3),
        gradient: const LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xFFEFF6F1),
            Color(0xFFD7E6DC),
          ],
        ),
        border: Border.all(color: const Color(0xFFBFD0C5)),
      ),
    );
  }
}
