import 'dart:math' as math;

import 'package:flutter/material.dart';

/// Soft, parlak, iki renkli gercekci kapsul.
class RealisticCapsule extends StatelessWidget {
  const RealisticCapsule({
    super.key,
    required this.width,
    required this.height,
    required this.leftColor,
    required this.rightColor,
    this.opacity = 1.0,
  });

  final double width;
  final double height;
  final Color leftColor;
  final Color rightColor;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: opacity.clamp(0.0, 1.0),
      child: Container(
        width: width,
        height: height,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(height),
          border: Border.all(
            color: Colors.black.withValues(alpha: 0.07),
            width: 0.9,
          ),
          boxShadow: [
            BoxShadow(
              color: leftColor.withValues(alpha: 0.48),
              blurRadius: height * 0.6,
              offset: Offset(0, height * 0.3),
            ),
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: height * 0.4,
              offset: Offset(0, height * 0.2),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(height),
          child: Stack(
            fit: StackFit.expand,
            children: [
              Row(
                children: [
                  Expanded(
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Color.lerp(leftColor, Colors.white, 0.2)!,
                            leftColor,
                            Color.lerp(leftColor, Colors.black, 0.2)!,
                          ],
                        ),
                      ),
                    ),
                  ),
                  Expanded(
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Color.lerp(rightColor, Colors.white, 0.15)!,
                            rightColor,
                            Color.lerp(rightColor, Colors.black, 0.14)!,
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              Align(
                alignment: Alignment.center,
                child: Container(
                  width: 2.2,
                  height: height * 0.84,
                  color: Colors.black.withValues(alpha: 0.14),
                ),
              ),
              Positioned(
                left: width * 0.1,
                top: height * 0.14,
                child: Container(
                  width: width * 0.36,
                  height: height * 0.24,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(999),
                    gradient: LinearGradient(
                      colors: [
                        Colors.white.withValues(alpha: 0.78),
                        Colors.white.withValues(alpha: 0.0),
                      ],
                    ),
                  ),
                ),
              ),
              Positioned(
                right: width * 0.12,
                top: height * 0.16,
                child: Container(
                  width: width * 0.24,
                  height: height * 0.18,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(999),
                    color: Colors.white.withValues(alpha: 0.45),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class CapsulePalette {
  const CapsulePalette(this.left, this.right);

  final Color left;
  final Color right;

  /// Soft ama ekranda net gorunen kapsul renkleri (biraz daha koyu).
  static const soft = <CapsulePalette>[
    CapsulePalette(Color(0xFF3A9FBF), Color(0xFFD9CFBE)),
    CapsulePalette(Color(0xFFD4A820), Color(0xFFF2D98A)),
    CapsulePalette(Color(0xFFB8926C), Color(0xFFE2D5C6)),
    CapsulePalette(Color(0xFF3EAD90), Color(0xFFB5E0CE)),
    CapsulePalette(Color(0xFF6A80C2), Color(0xFFC9C3E0)),
    CapsulePalette(Color(0xFFC97460), Color(0xFFF0C8BB)),
    CapsulePalette(Color(0xFF3FA3BF), Color(0xFFB0D8E4)),
  ];
}

/// Sayfa arkasi: soft renkli, gercekci hareketli kapsul arka plani.
class CapsuleBackground extends StatefulWidget {
  const CapsuleBackground({
    super.key,
    required this.child,
    this.capsuleCount = 12,
  });

  final Widget child;
  final int capsuleCount;

  @override
  State<CapsuleBackground> createState() => _CapsuleBackgroundState();
}

class _CapsuleBackgroundState extends State<CapsuleBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late List<_FloatingCapsule> _capsules;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 14),
    )..repeat();
    _capsules = _seedCapsules(widget.capsuleCount);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  List<_FloatingCapsule> _seedCapsules(int count) {
    final rng = math.Random(42);
    return List.generate(count, (i) {
      final palette = CapsulePalette.soft[i % CapsulePalette.soft.length];
      return _FloatingCapsule(
        x: 0.08 + rng.nextDouble() * 0.84,
        y: 0.06 + rng.nextDouble() * 0.88,
        size: 20 + rng.nextDouble() * 22,
        phase: rng.nextDouble() * math.pi * 2,
        speed: 0.35 + rng.nextDouble() * 0.55,
        tilt: -0.9 + rng.nextDouble() * 1.8,
        palette: palette,
        opacity: 0.9 + rng.nextDouble() * 0.1,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        const DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Color(0xFFF7FAFC),
                Color(0xFFF2F6F8),
                Color(0xFFF8FAFB),
              ],
            ),
          ),
        ),
        AnimatedBuilder(
          animation: _controller,
          builder: (context, _) {
            final t = _controller.value * 2 * math.pi;
            final size = MediaQuery.sizeOf(context);

            return Stack(
              children: [
                for (final c in _capsules)
                  Positioned(
                    left: c.x * size.width +
                        math.sin(t * c.speed + c.phase) * 18 -
                        c.size,
                    top: c.y * size.height +
                        math.cos(t * c.speed * 0.85 + c.phase) * 14 -
                        c.size * 0.4,
                    child: Transform.rotate(
                      angle:
                          c.tilt + math.sin(t * c.speed + c.phase) * 0.18,
                      child: RealisticCapsule(
                        width: c.size * 1.9,
                        height: c.size * 0.72,
                        leftColor: c.palette.left,
                        rightColor: c.palette.right,
                        opacity: c.opacity,
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
        widget.child,
      ],
    );
  }
}

class _FloatingCapsule {
  const _FloatingCapsule({
    required this.x,
    required this.y,
    required this.size,
    required this.phase,
    required this.speed,
    required this.tilt,
    required this.palette,
    required this.opacity,
  });

  final double x;
  final double y;
  final double size;
  final double phase;
  final double speed;
  final double tilt;
  final CapsulePalette palette;
  final double opacity;
}
