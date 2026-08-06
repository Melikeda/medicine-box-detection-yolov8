import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../l10n/app_localizations.dart';
import '../theme/app_colors.dart';

/// Üstte küçük TR / EN dil anahtarı.
class LanguageToggle extends StatelessWidget {
  const LanguageToggle({super.key});

  @override
  Widget build(BuildContext context) {
    final locale = context.locale;
    final isTr = locale.isTurkish;

    return Material(
      color: Colors.white.withValues(alpha: 0.92),
      elevation: 1,
      shadowColor: Colors.black26,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.all(3),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.divider),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _LangChip(
              label: 'TR',
              selected: isTr,
              onTap: () => locale.setLanguage(AppLanguage.tr),
            ),
            _LangChip(
              label: 'EN',
              selected: !isTr,
              onTap: () => locale.setLanguage(AppLanguage.en),
            ),
          ],
        ),
      ),
    );
  }
}

class _LangChip extends StatelessWidget {
  const _LangChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: selected
              ? AppColors.medicineGreen.withValues(alpha: 0.14)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          label,
          style: GoogleFonts.poppins(
            fontSize: 11,
            fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
            color: selected
                ? AppColors.medicineGreenDark
                : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }
}
