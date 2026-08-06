import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Sağ-sola dönen 3B ilaç kutusu (marka adı okunamaz, generic yazilar).
class AnimatedMedicineBox3D extends StatefulWidget {
  const AnimatedMedicineBox3D({
    super.key,
    this.width = 120,
    this.height = 148,
  });

  final double width;
  final double height;

  @override
  State<AnimatedMedicineBox3D> createState() => _AnimatedMedicineBox3DState();
}

class _AnimatedMedicineBox3DState extends State<AnimatedMedicineBox3D>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _rotationY;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 3200),
    )..repeat(reverse: true);

    _rotationY = Tween<double>(
      begin: -0.42,
      end: 0.42,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final w = widget.width;
    final h = widget.height;

    return SizedBox(
      width: w * 1.35,
      height: h * 1.15,
      child: AnimatedBuilder(
        animation: _rotationY,
        builder: (context, child) {
          final angle = _rotationY.value;
          final depth = w * 0.22;
          final sideShift = math.sin(angle) * depth * 0.45;

          return Stack(
            alignment: Alignment.center,
            children: [
              Positioned(
                bottom: h * 0.02,
                child: Transform(
                  transform: Matrix4.identity()
                    ..setEntry(3, 2, 0.001)
                    ..rotateX(-1.1)
                    ..rotateY(angle * 0.3),
                  alignment: Alignment.center,
                  child: Container(
                    width: w * 0.85,
                    height: h * 0.12,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(999),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.teal.withValues(alpha: 0.22),
                          blurRadius: 18,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              Transform(
                transform: Matrix4.identity()
                  ..setEntry(3, 2, 0.0018)
                  ..rotateY(angle),
                alignment: Alignment.center,
                child: Stack(
                  alignment: Alignment.center,
                  clipBehavior: Clip.none,
                  children: [
                    if (angle >= 0)
                      Transform.translate(
                        offset: Offset(sideShift + depth * 0.35, 0),
                        child: _BoxSideFace(
                          width: depth,
                          height: h,
                          darken: angle > 0,
                        ),
                      ),
                    _BoxFrontFace(width: w, height: h),
                    if (angle < 0)
                      Transform.translate(
                        offset: Offset(sideShift - depth * 0.35, 0),
                        child: _BoxSideFace(
                          width: depth,
                          height: h,
                          darken: angle < 0,
                        ),
                      ),
                    Transform.translate(
                      offset: Offset(0, -h * 0.48),
                      child: Transform(
                        transform: Matrix4.identity()
                          ..setEntry(3, 2, 0.002)
                          ..rotateX(-1.25)
                          ..rotateY(angle * 0.5),
                        alignment: Alignment.bottomCenter,
                        child: _BoxTopFace(width: w, depth: depth),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _BoxFrontFace extends StatelessWidget {
  const _BoxFrontFace({required this.width, required this.height});

  final double width;
  final double height;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFF8FDFF),
            Color(0xFFE8F7F7),
            Color(0xFFD6F0F0),
          ],
        ),
        border: Border.all(color: AppColors.teal.withValues(alpha: 0.25)),
        boxShadow: [
          BoxShadow(
            color: AppColors.teal.withValues(alpha: 0.18),
            blurRadius: 16,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: EdgeInsets.all(width * 0.08),
          child: FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.topCenter,
            child: SizedBox(
              width: width * 0.84,
              height: height * 0.88,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: width * 0.16,
                        height: width * 0.16,
                        decoration: BoxDecoration(
                          color: AppColors.teal.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Icon(
                          Icons.add,
                          size: width * 0.11,
                          color: AppColors.teal,
                        ),
                      ),
                      const Spacer(),
                      _BlurBar(width: width * 0.26, height: 6),
                    ],
                  ),
                  SizedBox(height: height * 0.045),
                  _BlurBar(width: width * 0.7, height: 9),
                  SizedBox(height: height * 0.03),
                  _BlurBar(width: width * 0.52, height: 7),
                  SizedBox(height: height * 0.04),
                  Container(
                    height: height * 0.36,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.55),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: AppColors.teal.withValues(alpha: 0.12),
                      ),
                    ),
                    padding: EdgeInsets.all(width * 0.05),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _BlurBar(width: width * 0.48, height: 5),
                        SizedBox(height: height * 0.018),
                        _BlurBar(width: width * 0.58, height: 5),
                        SizedBox(height: height * 0.018),
                        _BlurBar(width: width * 0.4, height: 5),
                        const Spacer(),
                        Row(
                          children: [
                            _BlurBar(width: width * 0.18, height: 11),
                            const Spacer(),
                            Icon(
                              Icons.medication_liquid_outlined,
                              size: width * 0.13,
                              color: AppColors.teal.withValues(alpha: 0.45),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: height * 0.03),
                  Center(child: _BlurBar(width: width * 0.32, height: 5)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _BoxSideFace extends StatelessWidget {
  const _BoxSideFace({
    required this.width,
    required this.height,
    required this.darken,
  });

  final double width;
  final double height;
  final bool darken;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height * 0.96,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(4),
        gradient: LinearGradient(
          begin: darken ? Alignment.centerLeft : Alignment.centerRight,
          end: darken ? Alignment.centerRight : Alignment.centerLeft,
          colors: [
            AppColors.tealDark.withValues(alpha: 0.55),
            AppColors.teal.withValues(alpha: 0.35),
          ],
        ),
      ),
    );
  }
}

class _BoxTopFace extends StatelessWidget {
  const _BoxTopFace({required this.width, required this.depth});

  final double width;
  final double depth;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width * 0.98,
      height: depth,
      decoration: BoxDecoration(
        color: AppColors.pastelMint.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: AppColors.teal.withValues(alpha: 0.2)),
      ),
    );
  }
}

class _BlurBar extends StatelessWidget {
  const _BlurBar({required this.width, required this.height});

  final double width;
  final double height;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(height),
        gradient: LinearGradient(
          colors: [
            AppColors.teal.withValues(alpha: 0.35),
            AppColors.teal.withValues(alpha: 0.18),
          ],
        ),
      ),
    );
  }
}
