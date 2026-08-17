import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../models/explain_response.dart';
import '../services/analyze_api_exception.dart';
import '../services/explain_api_service.dart';

class MedicineExplanationSection extends StatefulWidget {
  const MedicineExplanationSection({
    super.key,
    required this.medicineId,
    required this.medicineName,
    this.category,
    this.activeIngredient,
    this.dosage,
    this.form,
    ExplainApiService? apiService,
  }) : _apiService = apiService;

  final String medicineId;
  final String medicineName;
  final String? category;
  final String? activeIngredient;
  final String? dosage;
  final String? form;
  final ExplainApiService? _apiService;

  @override
  State<MedicineExplanationSection> createState() =>
      _MedicineExplanationSectionState();
}

class _MedicineExplanationSectionState
    extends State<MedicineExplanationSection> {
  ExplainApiService? _ownedService;
  ExplainResponse? _response;
  bool _loading = false;
  bool _expanded = false;

  ExplainApiService get _service =>
      widget._apiService ?? (_ownedService ??= ExplainApiService());

  @override
  void dispose() {
    _ownedService?.dispose();
    super.dispose();
  }

  Future<void> _loadExplanation() async {
    if (_loading || _response != null) {
      return;
    }

    setState(() {
      _loading = true;
    });

    try {
      final response = await _service.fetchExplanation(
        medicineId: widget.medicineId,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _response = response;
        _loading = false;
      });
    } on AnalyzeApiException {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _response = _catalogFallback();
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _response = _catalogFallback();
      });
    }
  }

  ExplainResponse _catalogFallback() {
    return ExplainResponse.catalogFallback(
      medicineId: widget.medicineId,
      medicineName: widget.medicineName,
      category: widget.category,
      activeIngredient: widget.activeIngredient,
      dose: widget.dosage,
      form: widget.form,
      disclaimer: context.s.medicineExplanationDisclaimer,
    );
  }

  void _onExpansionChanged(bool expanded) {
    setState(() => _expanded = expanded);
    if (expanded) {
      _loadExplanation();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Theme(
      data: theme.copyWith(dividerColor: Colors.transparent),
      child: ExpansionTile(
        initiallyExpanded: _expanded,
        onExpansionChanged: _onExpansionChanged,
        tilePadding: EdgeInsets.zero,
        childrenPadding: const EdgeInsets.only(top: 8, bottom: 4),
        leading: Icon(
          Icons.auto_awesome_outlined,
          color: theme.colorScheme.primary,
          size: 22,
        ),
        title: Text(
          context.s.aboutMedicine,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        subtitle: Text(
          widget.medicineName,
          style: theme.textTheme.bodySmall,
        ),
        children: [
          if (_loading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 12),
              child: Center(
                child: SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            )
          else if (_response != null)
            _ExplanationContent(response: _response!),
        ],
      ),
    );
  }
}

class _ExplanationContent extends StatelessWidget {
  const _ExplanationContent({required this.response});

  final ExplainResponse response;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final s = context.s;
    final summary = response.summary.trim().isNotEmpty
        ? response.summary.trim()
        : response.explanation.trim();
    final usage = response.usage.trim();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (summary.isNotEmpty) ...[
          _SectionHeader(
            icon: Icons.medication_outlined,
            title: s.medicineUsedForTitle,
          ),
          const SizedBox(height: 6),
          Text(summary, style: theme.textTheme.bodyMedium),
          if (usage.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(usage, style: theme.textTheme.bodyMedium),
          ],
          const SizedBox(height: 14),
        ],
        if (response.commonUses.isNotEmpty) ...[
          _SectionHeader(
            icon: Icons.playlist_add_check_outlined,
            title: s.medicineCommonUsesTitle,
          ),
          const SizedBox(height: 6),
          ...response.commonUses.map(
            (item) => _BulletRow(text: item),
          ),
          const SizedBox(height: 14),
        ],
        if (response.warnings.isNotEmpty) ...[
          _SectionHeader(
            icon: Icons.warning_amber_outlined,
            title: s.medicineWarningsTitle,
          ),
          const SizedBox(height: 6),
          ...response.warnings.map(
            (item) => _BulletRow(text: item),
          ),
          const SizedBox(height: 12),
        ],
        if (!response.hasStructuredContent && summary.isEmpty)
          Text(
            s.medicineExplanationFallback,
            style: theme.textTheme.bodyMedium,
          ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.info_outline,
              size: 16,
              color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
            ),
            const SizedBox(width: 6),
            Expanded(
              child: Text(
                response.disclaimer.isNotEmpty
                    ? response.disclaimer
                    : s.medicineExplanationDisclaimer,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.icon,
    required this.title,
  });

  final IconData icon;
  final String title;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        Icon(icon, size: 18, color: theme.colorScheme.primary),
        const SizedBox(width: 6),
        Expanded(
          child: Text(
            title,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
              color: theme.colorScheme.primary,
            ),
          ),
        ),
      ],
    );
  }
}

class _BulletRow extends StatelessWidget {
  const _BulletRow({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '•  ',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.primary,
            ),
          ),
          Expanded(
            child: Text(text, style: theme.textTheme.bodyMedium),
          ),
        ],
      ),
    );
  }
}
