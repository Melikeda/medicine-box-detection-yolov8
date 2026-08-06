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
    ExplainApiService? apiService,
  }) : _apiService = apiService;

  final String medicineId;
  final String medicineName;
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
  String? _error;
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
      _error = null;
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
    } on AnalyzeApiException catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = exc.message;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = 'Aciklama yuklenemedi.';
      });
    }
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
          else if (_error != null)
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _error!,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.error,
                  ),
                ),
                const SizedBox(height: 8),
                TextButton.icon(
                  onPressed: () {
                    setState(() => _response = null);
                    _loadExplanation();
                  },
                  icon: const Icon(Icons.refresh),
                  label: const Text('Tekrar dene'),
                ),
              ],
            )
          else if (_response != null) ...[
            Text(
              _response!.explanation,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 8),
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
                    _response!.disclaimer,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
