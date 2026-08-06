import 'package:flutter/material.dart';

import 'capsule_background.dart';

/// Eski pastel blob arka planinin yerine soft gercekci kapsul arka plani.
class AnimatedPastelBackground extends StatelessWidget {
  const AnimatedPastelBackground({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return CapsuleBackground(capsuleCount: 12, child: child);
  }
}
