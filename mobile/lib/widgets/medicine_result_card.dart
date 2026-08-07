import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../models/medicine_box_result.dart';
import '../theme/app_colors.dart';
import '../utils/medicine_display.dart';
import 'medicine_explanation_section.dart';

class MedicineResultCard extends StatelessWidget {
  const MedicineResultCard({
    super.key,
    required this.result,
  });

  final MedicineBoxResult result;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final s = context.s;
    final statusColor = _statusColor(theme, result.status);

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: statusColor.withValues(alpha: 0.12)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(_statusIcon(result.status), color: statusColor),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    MedicineDisplay.boxLabel(result.boxIndex, strings: s),
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    _statusLabel(result.status, s),
                    style: TextStyle(
                      color: statusColor,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              result.displayMessage,
              style: theme.textTheme.bodyLarge,
            ),
            if (result.isMatched) ...[
              const SizedBox(height: 12),
              _InfoRow(
                label: s.medicineLabel,
                value: result.medicineName ?? '-',
              ),
              _InfoRow(
                label: s.matchScoreLabel,
                value: '${result.matchingScore.toStringAsFixed(1)}%',
              ),
              if (MedicineDisplay.shouldShowField(
                result.activeIngredient,
                strings: s,
              ))
                _InfoRow(
                  label: s.activeIngredientLabel,
                  value: MedicineDisplay.formatField(
                    result.activeIngredient,
                    strings: s,
                  )!,
                ),
              if (MedicineDisplay.shouldShowField(result.dosage, strings: s))
                _InfoRow(
                  label: s.dosageLabel,
                  value: MedicineDisplay.formatField(
                    result.dosage,
                    strings: s,
                  )!,
                ),
              if (MedicineDisplay.shouldShowField(result.form, strings: s))
                _InfoRow(
                  label: s.formLabel,
                  value: MedicineDisplay.formatField(
                    result.form,
                    strings: s,
                  )!,
                ),
              if (MedicineDisplay.shouldShowField(result.category, strings: s))
                _InfoRow(
                  label: s.categoryLabel,
                  value: MedicineDisplay.formatField(
                    result.category,
                    strings: s,
                  )!,
                ),
              if (result.medicineId != null &&
                  result.medicineId!.isNotEmpty) ...[
                const SizedBox(height: 12),
                const Divider(height: 1),
                const SizedBox(height: 4),
                MedicineExplanationSection(
                  medicineId: result.medicineId!,
                  medicineName: result.medicineName ?? s.medicineLabel,
                ),
              ],
            ] else if (result.bestCandidate != null &&
                result.bestCandidate!.isNotEmpty) ...[
              const SizedBox(height: 8),
              _InfoRow(
                label: s.nearestCandidateLabel,
                value: result.bestCandidate!,
              ),
            ],
            if (result.ocrText != null && result.ocrText!.isNotEmpty) ...[
              const SizedBox(height: 8),
              _InfoRow(label: s.ocrLabel, value: result.ocrText!),
            ],
          ],
        ),
      ),
    );
  }

  Color _statusColor(ThemeData theme, String status) {
    switch (status) {
      case 'matched':
        return AppColors.success;
      case 'not_found':
        return AppColors.warning;
      case 'not_medicine_box':
        return AppColors.textSecondary;
      default:
        return theme.colorScheme.error;
    }
  }

  IconData _statusIcon(String status) {
    switch (status) {
      case 'matched':
        return Icons.check_circle_outline;
      case 'not_found':
        return Icons.help_outline;
      case 'not_medicine_box':
        return Icons.hide_image_outlined;
      default:
        return Icons.error_outline;
    }
  }

  String _statusLabel(String status, AppStrings s) {
    switch (status) {
      case 'matched':
        return s.statusMatched;
      case 'not_found':
        return s.statusNotFound;
      case 'not_medicine_box':
        return s.statusNotBox;
      default:
        return s.statusError;
    }
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(
              label,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
              ),
            ),
          ),
          Expanded(
            child: Text(value, style: theme.textTheme.bodyMedium),
          ),
        ],
      ),
    );
  }
}
