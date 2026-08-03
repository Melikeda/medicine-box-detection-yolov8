import 'package:flutter/material.dart';

import '../models/analyze_response.dart';
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

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analiz Sonucu'),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Ozet',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _SummaryChip(
                          label: 'Tespit',
                          value: '${response.detectionCount}',
                          color: theme.colorScheme.primary,
                        ),
                        _SummaryChip(
                          label: 'Eslesti',
                          value: '${summary.matchedCount}',
                          color: Colors.green.shade700,
                        ),
                        _SummaryChip(
                          label: 'Bulunamadi',
                          value: '${summary.notFoundCount}',
                          color: Colors.orange.shade800,
                        ),
                        if (summary.notMedicineBoxCount > 0)
                          _SummaryChip(
                            label: 'Kutu degil',
                            value: '${summary.notMedicineBoxCount}',
                            color: Colors.blueGrey,
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
            ),
            const SizedBox(height: 16),
            if (response.medicines.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    response.detectionCount == 0
                        ? 'Fotografta ilac kutusu tespit edilemedi.'
                        : 'Sonuc listesi bos dondu.',
                    style: theme.textTheme.bodyLarge,
                  ),
                ),
              )
            else
              ...response.medicines.map(
                (result) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: MedicineResultCard(result: result),
                ),
              ),
            const SizedBox(height: 8),
            if (response.disclaimer != null && response.disclaimer!.isNotEmpty)
              Card(
                color: theme.colorScheme.surfaceContainerHighest,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.info_outline,
                        size: 20,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          response.disclaimer!,
                          style: theme.textTheme.bodySmall,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            if (response.disclaimer != null && response.disclaimer!.isNotEmpty)
              const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).popUntil(
                  (route) => route.settings.name == '/home' || route.isFirst,
                );
              },
              icon: const Icon(Icons.home),
              label: const Text('Ana Sayfaya Don'),
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
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        '$label: $value',
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
