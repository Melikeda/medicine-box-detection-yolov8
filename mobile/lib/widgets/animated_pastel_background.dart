import 'package:flutter/material.dart';

import 'capsule_background.dart';

/// Soft realistic capsule background that replaced the old pastel blobs.
class AnimatedPastelBackground extends StatelessWidget {
  const AnimatedPastelBackground({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return CapsuleBackground(capsuleCount: 12, child: child);
  }
}
