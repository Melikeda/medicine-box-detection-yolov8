import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

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
        color: Colors.white,
        borderRadius: BorderRadius.circular(size * 0.28),
        boxShadow: showShadow
            ? [
                BoxShadow(
                  color: AppColors.accent.withValues(alpha: 0.15),
                  blurRadius: 24,
                  offset: const Offset(0, 12),
                ),
              ]
            : null,
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          Container(
            width: size * 0.72,
            height: size * 0.72,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  AppColors.pastelSky,
                  AppColors.pastelMint,
                ],
              ),
              borderRadius: BorderRadius.circular(size * 0.22),
            ),
          ),
          Icon(
            Icons.medication_liquid_outlined,
            size: size * 0.42,
            color: AppColors.teal,
          ),
          Positioned(
            right: size * 0.16,
            bottom: size * 0.16,
            child: Container(
              padding: EdgeInsets.all(size * 0.06),
              decoration: const BoxDecoration(
                color: AppColors.tealDark,
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.photo_camera_outlined,
                size: size * 0.16,
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
