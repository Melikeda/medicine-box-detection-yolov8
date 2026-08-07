import 'dart:convert';
import 'dart:io';

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

import '../models/analyze_response.dart';
import '../models/analyze_summary.dart';
import '../models/scan_history_entry.dart';

/// Yerel tarama gecmisi — cihazda SQLite; analiz API hizini etkilemez.
class ScanHistoryService {
  ScanHistoryService({
    Future<Database> Function()? openDatabase,
    Future<Directory> Function()? documentsDirectory,
    this.maxEntries = 50,
  })  : _openDatabase = openDatabase ?? _defaultOpenDatabase,
        _documentsDirectory = documentsDirectory ?? getApplicationDocumentsDirectory;

  static const _dbName = 'scan_history.db';
  static const _tableName = 'scan_history';

  final Future<Database> Function()? _openDatabase;
  final Future<Directory> Function() _documentsDirectory;
  final int maxEntries;

  Database? _database;

  Future<Database> _db() async {
    _database ??= await _openDatabase!();
    return _database!;
  }

  Future<void> close() async {
    final db = _database;
    _database = null;
    if (db != null) {
      await db.close();
    }
  }

  static Future<Database> _defaultOpenDatabase() async {
    final documentsDir = await getApplicationDocumentsDirectory();
    final dbPath = p.join(documentsDir.path, _dbName);
    return openDatabase(
      dbPath,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE $_tableName (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at INTEGER NOT NULL,
            detection_count INTEGER NOT NULL,
            matched_count INTEGER NOT NULL,
            preview_label TEXT NOT NULL,
            image_path TEXT,
            response_json TEXT NOT NULL
          )
        ''');
      },
    );
  }

  /// Analiz bittikten sonra arka planda cagirilir; await zorunlu degil.
  Future<void> saveScan({
    required AnalyzeResponse response,
    String? imagePath,
  }) async {
    if (!response.success) {
      return;
    }

    final db = await _db();
    final createdAt = DateTime.now();
    final storedImagePath = await _persistImage(
      sourcePath: imagePath,
      createdAt: createdAt,
    );

    await db.insert(
      _tableName,
      {
        'created_at': createdAt.millisecondsSinceEpoch,
        'detection_count': response.detectionCount,
        'matched_count': response.summary.matchedCount,
        'preview_label': _buildPreviewLabel(response),
        'image_path': storedImagePath,
        'response_json': jsonEncode(response.toJson()),
      },
    );

    await _trimOldEntries(db);
  }

  Future<List<ScanHistoryEntry>> listScans({int? limit}) async {
    final db = await _db();
    final rows = await db.query(
      _tableName,
      orderBy: 'created_at DESC',
      limit: limit,
    );

    return rows.map(_entryFromRow).toList();
  }

  Future<ScanHistoryEntry?> getScan(int id) async {
    final db = await _db();
    final rows = await db.query(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );
    if (rows.isEmpty) {
      return null;
    }
    return _entryFromRow(rows.first);
  }

  Future<void> deleteScan(int id) async {
    final db = await _db();
    final rows = await db.query(
      _tableName,
      columns: ['image_path'],
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );

    await db.delete(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
    );

    final imagePath = rows.firstOrNull?['image_path'] as String?;
    if (imagePath != null && imagePath.isNotEmpty) {
      final file = File(imagePath);
      if (await file.exists()) {
        await file.delete();
      }
    }
  }

  Future<void> clearAll() async {
    final db = await _db();
    final rows = await db.query(_tableName, columns: ['image_path']);
    await db.delete(_tableName);

    for (final row in rows) {
      final imagePath = row['image_path'] as String?;
      if (imagePath == null || imagePath.isEmpty) {
        continue;
      }
      final file = File(imagePath);
      if (await file.exists()) {
        await file.delete();
      }
    }
  }

  ScanHistoryEntry _entryFromRow(Map<String, Object?> row) {
    final responseJson = row['response_json'] as String? ?? '{}';
    final decoded = jsonDecode(responseJson);
    final response = decoded is Map<String, dynamic>
        ? AnalyzeResponse.fromJson(decoded)
        : const AnalyzeResponse(
            success: false,
            detectionCount: 0,
            medicines: [],
            summary: AnalyzeSummary(),
            ocrMode: 'fast',
            processingTimeMs: 0,
          );

    return ScanHistoryEntry(
      id: row['id'] as int? ?? 0,
      createdAt: DateTime.fromMillisecondsSinceEpoch(
        row['created_at'] as int? ?? 0,
      ),
      detectionCount: row['detection_count'] as int? ?? 0,
      matchedCount: row['matched_count'] as int? ?? 0,
      previewLabel: row['preview_label'] as String? ?? 'Tarama',
      imagePath: row['image_path'] as String?,
      response: response,
    );
  }

  Future<String?> _persistImage({
    required String? sourcePath,
    required DateTime createdAt,
  }) async {
    if (sourcePath == null || sourcePath.isEmpty) {
      return null;
    }

    final source = File(sourcePath);
    if (!await source.exists()) {
      return null;
    }

    final documentsDir = await _documentsDirectory();
    final historyDir = Directory(p.join(documentsDir.path, 'scan_history'));
    if (!await historyDir.exists()) {
      await historyDir.create(recursive: true);
    }

    final extension = p.extension(sourcePath).isEmpty ? '.jpg' : p.extension(sourcePath);
    final targetPath = p.join(
      historyDir.path,
      '${createdAt.millisecondsSinceEpoch}$extension',
    );
    await source.copy(targetPath);
    return targetPath;
  }

  String _buildPreviewLabel(AnalyzeResponse response) {
    final matchedNames = response.medicines
        .where((item) => item.isMatched && item.medicineName != null)
        .map((item) => item.medicineName!)
        .take(2)
        .toList();

    if (matchedNames.isNotEmpty) {
      final suffix = response.summary.matchedCount > matchedNames.length
          ? ' +${response.summary.matchedCount - matchedNames.length}'
          : '';
      return '${matchedNames.join(', ')}$suffix';
    }

    if (response.detectionCount == 0) {
      return 'Kutu tespit edilemedi';
    }

    return '${response.detectionCount} kutu tarandi';
  }

  Future<void> _trimOldEntries(Database db) async {
    final count = Sqflite.firstIntValue(
      await db.rawQuery('SELECT COUNT(*) FROM $_tableName'),
    );
    if (count == null || count <= maxEntries) {
      return;
    }

    final overflow = count - maxEntries;
    final rows = await db.query(
      _tableName,
      columns: ['id', 'image_path'],
      orderBy: 'created_at ASC',
      limit: overflow,
    );

    for (final row in rows) {
      await deleteScan(row['id'] as int);
    }
  }
}

extension _FirstOrNull<E> on List<E> {
  E? get firstOrNull => isEmpty ? null : first;
}
