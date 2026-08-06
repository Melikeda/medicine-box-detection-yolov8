import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../models/analyze_response.dart';
import '../theme/app_colors.dart';
import '../widgets/empty_state.dart';
import '../widgets/medicine_result_card.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({
    super.key,
    required this.response,
    this.imagePath,
  });

  final AnalyzeResponse response;
  final String? imagePath;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final summary = response.summary;
    final s = context.s;

    return Scaffold(
      appBar: AppBar(
        title: Text(s.analyzeResult),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    s.summary,
                    style: theme.textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _SummaryChip(
                        label: s.detected,
                        value: '${response.detectionCount}',
                        color: AppColors.accent,
                      ),
                      _SummaryChip(
                        label: s.matched,
                        value: '${summary.matchedCount}',
                        color: AppColors.success,
                      ),
                      _SummaryChip(
                        label: s.notFound,
                        value: '${summary.notFoundCount}',
                        color: AppColors.warning,
                      ),
                      if (summary.notMedicineBoxCount > 0)
                        _SummaryChip(
                          label: s.notBox,
                          value: '${summary.notMedicineBoxCount}',
                          color: AppColors.textSecondary,
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Sure: ${(response.processingTimeMs / 1000).toStringAsFixed(1)} sn'
                    ' · OCR: ${response.ocrMode}',
                    style: theme.textTheme.bodySmall,
                  ),
                  if (response.error != null && response.error!.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      response.error!,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.error,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 20),
            if (response.medicines.isEmpty)
              EmptyState(
                icon: Icons.search_off_rounded,
                title: response.detectionCount == 0
                    ? s.noBoxFound
                    : s.noResult,
                message: response.detectionCount == 0
                    ? s.noBoxHint
                    : s.noResult,
              )
            else ...[
              Text(
                s.detectedBoxes,
                style: theme.textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              ...response.medicines.map(
                (result) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: MedicineResultCard(result: result),
                ),
              ),
            ],
            if (response.disclaimer != null && response.disclaimer!.isNotEmpty) ...[
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.warningCard,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.info_outline,
                      size: 20,
                      color: AppColors.warning,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        response.disclaimer!,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).popUntil(
                  (route) => route.settings.name == '/home' || route.isFirst,
                );
              },
              icon: const Icon(Icons.home_rounded),
              label: Text(s.backHome),
            ),
          ],
        ),
      ),
    );
  }
}

class _SummaryChip extends StatelessWidget {
  const _SummaryChip({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Text(
        '$label: $value',
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.w700,
          fontSize: 13,
        ),
      ),
    );
  }
}
