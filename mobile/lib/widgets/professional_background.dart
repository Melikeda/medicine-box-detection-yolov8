import 'package:flutter/material.dart';

import 'capsule_background.dart';

/// Soft animated capsule background used on the main screens.
class ProfessionalBackground extends StatelessWidget {
  const ProfessionalBackground({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return CapsuleBackground(child: child);
  }
}
