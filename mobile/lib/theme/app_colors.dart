import 'package:flutter/material.dart';

/// Yolocilin core palette: dark green plus light pastel green.
///
/// Note: background capsules and small capsule decorations keep their
/// colors in [CapsulePalette]; the colors here are used for
/// application chrome such as buttons, navigation, cards, and text.
class AppColors {
  AppColors._();

  /// Base pair.
  static const Color darkGreen = Color(0xFF1B4332);
  static const Color pastelGreen = Color(0xFFE8F5EE);

  static const Color background = Color(0xFFF3FAF5);
  static const Color surface = Colors.white;
  static const Color primary = darkGreen;

  /// Button/accent color, one shade lighter than dark green.
  static const Color teal = Color(0xFF2D6A4F);
  static const Color tealDark = darkGreen;
  static const Color accent = Color(0xFF40916C);
  static const Color accentLight = Color(0xFF74C69D);

  static const Color pastelBlue = Color(0xFFD8F3DC);
  static const Color pastelMint = pastelGreen;
  static const Color pastelSky = Color(0xFFF1F8F4);
  static const Color pastelAqua = Color(0xFFB7E4C7);

  static const Color cameraCard = pastelGreen;
  static const Color cameraIcon = Color(0xFF2D6A4F);
  static const Color galleryCard = Color(0xFFD8F3DC);
  static const Color galleryIcon = darkGreen;
  static const Color historyCard = pastelGreen;
  static const Color historyIcon = Color(0xFF2D6A4F);

  static const Color navActive = Color(0xFF2D6A4F);
  static const Color textSecondary = Color(0xFF5C6B63);
  static const Color divider = Color(0xFFD5E5DB);
  static const Color success = Color(0xFF2D6A4F);
  static const Color warning = Color(0xFFD97706);
  static const Color warningCard = Color(0xFFFFF8E1);

  static const Color medicineGreenDark = darkGreen;
  static const Color medicineGreen = Color(0xFF2D6A4F);
  static const Color medicineGreenLight = Color(0xFF52B788);
  static const Color medicineSage = Color(0xFF95D5B2);
}
