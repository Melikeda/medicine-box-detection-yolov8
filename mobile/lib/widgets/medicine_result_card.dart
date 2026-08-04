import 'package:flutter/material.dart';

import '../models/medicine_box_result.dart';
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
    final statusColor = _statusColor(theme, result.status);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(_statusIcon(result.status), color: statusColor),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    MedicineDisplay.boxLabel(result.boxIndex),
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Chip(
                  label: Text(_statusLabel(result.status)),
                  backgroundColor: statusColor.withValues(alpha: 0.12),
                  labelStyle: TextStyle(color: statusColor),
                  visualDensity: VisualDensity.compact,
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
                label: 'Ilac',
                value: result.medicineName ?? '-',
              ),
              _InfoRow(
                label: 'Eslesme skoru',
                value: '${result.matchingScore.toStringAsFixed(1)}%',
              ),
              if (MedicineDisplay.shouldShowField(result.activeIngredient))
                _InfoRow(
                  label: 'Etken madde',
                  value: MedicineDisplay.formatField(result.activeIngredient)!,
                ),
              if (MedicineDisplay.shouldShowField(result.dosage))
                _InfoRow(
                  label: 'Doz',
                  value: MedicineDisplay.formatField(result.dosage)!,
                ),
              if (MedicineDisplay.shouldShowField(result.form))
                _InfoRow(
                  label: 'Form',
                  value: MedicineDisplay.formatField(result.form)!,
                ),
              if (MedicineDisplay.shouldShowField(result.category))
                _InfoRow(
                  label: 'Kategori',
                  value: MedicineDisplay.formatField(result.category)!,
                ),
              if (result.medicineId != null &&
                  result.medicineId!.isNotEmpty) ...[
                const SizedBox(height: 12),
                const Divider(height: 1),
                const SizedBox(height: 4),
                MedicineExplanationSection(
                  medicineId: result.medicineId!,
                  medicineName: result.medicineName ?? 'Ilac',
                ),
              ],
            ] else if (result.bestCandidate != null &&
                result.bestCandidate!.isNotEmpty) ...[
              const SizedBox(height: 8),
              _InfoRow(label: 'En yakin aday', value: result.bestCandidate!),
            ],
            if (result.ocrText != null && result.ocrText!.isNotEmpty) ...[
              const SizedBox(height: 8),
              _InfoRow(label: 'OCR', value: result.ocrText!),
            ],
          ],
        ),
      ),
    );
  }

  Color _statusColor(ThemeData theme, String status) {
    switch (status) {
      case 'matched':
        return Colors.green.shade700;
      case 'not_found':
        return Colors.orange.shade800;
      case 'not_medicine_box':
        return Colors.blueGrey;
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

  String _statusLabel(String status) {
    switch (status) {
      case 'matched':
        return 'Eslesti';
      case 'not_found':
        return 'Bulunamadi';
      case 'not_medicine_box':
        return 'Kutu degil';
      default:
        return 'Hata';
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
