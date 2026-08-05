import 'package:flutter/material.dart';

import '../models/scan_history_entry.dart';
import '../routes/app_router.dart';
import '../services/scan_history_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({
    super.key,
    this.historyService,
  });

  final ScanHistoryService? historyService;

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
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

  Future<void> _openEntry(ScanHistoryEntry entry) async {
    await Navigator.of(context).pushNamed(
      AppRoutes.result,
      arguments: ResultRouteArgs(
        response: entry.response,
        imagePath: entry.imagePath,
      ),
    );
  }

  Future<void> _deleteEntry(ScanHistoryEntry entry) async {
    await _historyService.deleteScan(entry.id);
    if (!mounted) {
      return;
    }
    _reload();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Kayit silindi')),
    );
  }

  Future<void> _clearAll() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Gecmisi temizle'),
          content: const Text('Tum tarama kayitlari silinsin mi?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Iptal'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('Sil'),
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

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tarama Gecmisi'),
        actions: [
          IconButton(
            tooltip: 'Tumunu sil',
            onPressed: _clearAll,
            icon: const Icon(Icons.delete_sweep_outlined),
          ),
        ],
      ),
      body: FutureBuilder<List<ScanHistoryEntry>>(
        future: _entriesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Text('Gecmis yuklenemedi: ${snapshot.error}'),
            );
          }

          final entries = snapshot.data ?? const [];
          if (entries.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.history,
                      size: 56,
                      color: theme.colorScheme.primary.withValues(alpha: 0.7),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Henuz kayit yok',
                      style: theme.textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Basarili analizler otomatik olarak burada listelenir.',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(
                          alpha: 0.7,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: entries.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
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
                    borderRadius: BorderRadius.circular(12),
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
                          title: const Text('Kaydi sil'),
                          content: const Text('Bu tarama kaydi silinsin mi?'),
                          actions: [
                            TextButton(
                              onPressed: () =>
                                  Navigator.of(context).pop(false),
                              child: const Text('Iptal'),
                            ),
                            FilledButton(
                              onPressed: () =>
                                  Navigator.of(context).pop(true),
                              child: const Text('Sil'),
                            ),
                          ],
                        ),
                      ) ??
                      false;
                },
                onDismissed: (_) => _deleteEntry(entry),
                child: Card(
                  child: ListTile(
                    leading: CircleAvatar(
                      child: Text('${entry.detectionCount}'),
                    ),
                    title: Text(
                      entry.previewLabel,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    subtitle: Text(entry.subtitle),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => _openEntry(entry),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
