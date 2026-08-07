import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Yolocilin marka logosu — açık yeşil kapsül + yolocilin yazısı.
class AppLogo extends StatelessWidget {
  const AppLogo({
    super.key,
    this.size = 96,
    this.showShadow = true,
  });

  final double size;
  final bool showShadow;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(size * 0.28),
        boxShadow: showShadow
            ? [
                BoxShadow(
                  color: AppColors.darkGreen.withValues(alpha: 0.16),
                  blurRadius: 24,
                  offset: Offset(0, size * 0.1),
                ),
              ]
            : null,
      ),
      clipBehavior: Clip.antiAlias,
      child: Image.asset(
        'assets/branding/app_logo.png',
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) {
          return ColoredBox(
            color: AppColors.pastelGreen,
            child: Icon(
              Icons.medication_outlined,
              size: size * 0.45,
              color: AppColors.darkGreen,
            ),
          );
        },
      ),
    );
  }
}
