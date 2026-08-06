import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../models/scan_history_entry.dart';
import '../routes/app_router.dart';
import '../services/scan_history_service.dart';
import '../theme/app_colors.dart';
import '../widgets/animated_pastel_background.dart';
import '../widgets/empty_state.dart';
import '../widgets/language_toggle.dart';
import '../widgets/recent_scan_tile.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({
    super.key,
    this.historyService,
    this.embedded = false,
    this.onEntryOpened,
  });

  final ScanHistoryService? historyService;
  final bool embedded;
  final VoidCallback? onEntryOpened;

  @override
  State<HistoryScreen> createState() => HistoryScreenState();
}

class HistoryScreenState extends State<HistoryScreen> {
  late final ScanHistoryService _historyService;
  late Future<List<ScanHistoryEntry>> _entriesFuture;

  @override
  void initState() {
    super.initState();
    _historyService = widget.historyService ?? ScanHistoryService();
    _reload();
  }

  void _reload() {
    setState(() {
      _entriesFuture = _historyService.listScans();
    });
  }

  void reload() => _reload();

  Future<void> _openEntry(ScanHistoryEntry entry) async {
    await Navigator.of(context).pushNamed(
      AppRoutes.result,
      arguments: ResultRouteArgs(
        response: entry.response,
        imagePath: entry.imagePath,
      ),
    );
    widget.onEntryOpened?.call();
    _reload();
  }

  Future<void> _deleteEntry(ScanHistoryEntry entry) async {
    await _historyService.deleteScan(entry.id);
    if (!mounted) {
      return;
    }
    _reload();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(context.s.deleted)),
    );
  }

  Future<void> _clearAll() async {
    final s = context.s;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(s.clearHistory),
          content: Text(s.clearHistoryConfirm),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: Text(s.cancel),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: Text(s.delete),
            ),
          ],
        );
      },
    );

    if (confirmed != true) {
      return;
    }

    await _historyService.clearAll();
    if (!mounted) {
      return;
    }
    _reload();
  }

  Widget _buildBody() {
    final theme = Theme.of(context);
    final s = context.s;

    return FutureBuilder<List<ScanHistoryEntry>>(
      future: _entriesFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(
            child: Text('${s.historyLoadError}: ${snapshot.error}'),
          );
        }

        final entries = snapshot.data ?? const [];
        if (entries.isEmpty) {
          return Center(
            child: EmptyState(
              icon: Icons.history_rounded,
              title: s.historyEmptyTitle,
              message: s.historyEmptyBody,
            ),
          );
        }

        return ListView.separated(
          padding: EdgeInsets.fromLTRB(
            20,
            widget.embedded ? 8 : 16,
            20,
            24,
          ),
          itemCount: entries.length,
          separatorBuilder: (_, __) => const SizedBox(height: 10),
          itemBuilder: (context, index) {
            final entry = entries[index];
            return Dismissible(
              key: ValueKey(entry.id),
              direction: DismissDirection.endToStart,
              background: Container(
                alignment: Alignment.centerRight,
                padding: const EdgeInsets.only(right: 20),
                decoration: BoxDecoration(
                  color: theme.colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Icon(
                  Icons.delete_outline,
                  color: theme.colorScheme.onErrorContainer,
                ),
              ),
              confirmDismiss: (_) async {
                return await showDialog<bool>(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: Text(s.deleteEntry),
                        content: Text(s.deleteEntryConfirm),
                        actions: [
                          TextButton(
                            onPressed: () =>
                                Navigator.of(context).pop(false),
                            child: Text(s.cancel),
                          ),
                          FilledButton(
                            onPressed: () =>
                                Navigator.of(context).pop(true),
                            child: Text(s.delete),
                          ),
                        ],
                      ),
                    ) ??
                    false;
              },
              onDismissed: (_) => _deleteEntry(entry),
              child: RecentScanTile(
                entry: entry,
                onTap: () => _openEntry(entry),
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = context.s;

    if (widget.embedded) {
      return AnimatedPastelBackground(
        child: SafeArea(
          bottom: false,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 8, 12, 0),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        s.historyTitle,
                        style: Theme.of(context)
                            .textTheme
                            .headlineMedium
                            ?.copyWith(
                              fontSize: 24,
                              fontStyle: FontStyle.normal,
                              color: AppColors.primary,
                            ),
                      ),
                    ),
                    const LanguageToggle(),
                    IconButton(
                      tooltip: s.clearAllTooltip,
                      onPressed: _clearAll,
                      icon: const Icon(Icons.delete_sweep_outlined),
                    ),
                  ],
                ),
              ),
              Expanded(child: _buildBody()),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(s.historyTitle),
        actions: [
          IconButton(
            tooltip: s.clearAllTooltip,
            onPressed: _clearAll,
            icon: const Icon(Icons.delete_sweep_outlined),
          ),
        ],
      ),
      body: _buildBody(),
    );
  }
}
