import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../l10n/app_localizations.dart';
import '../models/ocr_mode.dart';
import '../theme/app_colors.dart';

/// Onizleme ekraninda Hizli / Hassas OCR secimi.
class OcrModeSelector extends StatelessWidget {
  const OcrModeSelector({
    super.key,
    required this.value,
    required this.onChanged,
    this.enabled = true,
  });

  final OcrMode value;
  final ValueChanged<OcrMode> onChanged;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final s = context.s;
    final description = value == OcrMode.fast
        ? s.ocrModeFastDescription
        : s.ocrModeAccurateDescription;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          s.ocrModeLabel,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: AppColors.primary,
          ),
        ),
        const SizedBox(height: 8),
        Opacity(
          opacity: enabled ? 1 : 0.55,
          child: IgnorePointer(
            ignoring: !enabled,
            child: Material(
              color: Colors.white,
              elevation: 0,
              borderRadius: BorderRadius.circular(16),
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.divider),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: _ModeChip(
                        label: s.ocrModeFast,
                        selected: value == OcrMode.fast,
                        onTap: () => onChanged(OcrMode.fast),
                      ),
                    ),
                    Expanded(
                      child: _ModeChip(
                        label: s.ocrModeAccurate,
                        selected: value == OcrMode.accurate,
                        onTap: () => onChanged(OcrMode.accurate),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          description,
          style: theme.textTheme.bodySmall?.copyWith(
            color: AppColors.textSecondary,
            height: 1.35,
          ),
        ),
      ],
    );
  }
}

class _ModeChip extends StatelessWidget {
  const _ModeChip({
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
      borderRadius: BorderRadius.circular(12),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(vertical: 10),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: selected
              ? AppColors.medicineGreen.withValues(alpha: 0.14)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          label,
          style: GoogleFonts.poppins(
            fontSize: 13,
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
