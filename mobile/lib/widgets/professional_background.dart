import 'package:flutter/material.dart';

import 'capsule_background.dart';

/// Soft hareketli kapsul arka plani (tum ana sayfalar).
class ProfessionalBackground extends StatelessWidget {
  const ProfessionalBackground({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return CapsuleBackground(child: child);
  }
}
