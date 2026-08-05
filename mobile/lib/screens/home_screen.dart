import 'dart:io';

import 'package:flutter/material.dart';

import '../config/app_config.dart';
import '../routes/app_router.dart';
import '../services/image_picker_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ImagePickerService _imagePickerService = ImagePickerService();

  String? _selectedImagePath;
  bool _isPicking = false;
  _PickSource? _activePickSource;

  Future<void> _pickFromGallery() {
    return _pickImage(
      source: _PickSource.gallery,
      picker: _imagePickerService.pickFromGallery,
      failureMessage: 'Galeri acilamadi',
    );
  }

  Future<void> _captureFromCamera() {
    return _pickImage(
      source: _PickSource.camera,
      picker: _imagePickerService.pickFromCamera,
      failureMessage: 'Kamera acilamadi',
    );
  }

  Future<void> _pickImage({
    required _PickSource source,
    required Future<String?> Function() picker,
    required String failureMessage,
  }) async {
    setState(() {
      _isPicking = true;
      _activePickSource = source;
    });

    try {
      final path = await picker();
      if (!mounted) {
        return;
      }

      if (path == null) {
        return;
      }

      setState(() => _selectedImagePath = path);
      await Navigator.of(context).pushNamed(
        AppRoutes.imagePreview,
        arguments: path,
      );
    } catch (error) {
      if (!mounted) {
        return;
      }
      _showError('$failureMessage: $error');
    } finally {
      if (mounted) {
        setState(() {
          _isPicking = false;
          _activePickSource = null;
        });
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text(AppConfig.appName),
        actions: [
          IconButton(
            tooltip: 'Tarama gecmisi',
            onPressed: () => Navigator.of(context).pushNamed(AppRoutes.history),
            icon: const Icon(Icons.history),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Icon(
                        Icons.medication_outlined,
                        size: 56,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Ilac kutusu fotografi',
                        textAlign: TextAlign.center,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Kameradan cekin veya galeriden secin, onizleyin ve '
                        'FastAPI backend uzerinde analiz ettirin.',
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
              ),
              const SizedBox(height: 20),
              if (_selectedImagePath != null) ...[
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: AspectRatio(
                    aspectRatio: 4 / 3,
                    child: Image.file(
                      File(_selectedImagePath!),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Son secim: ${_basename(_selectedImagePath!)}',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodySmall,
                ),
                const SizedBox(height: 20),
              ],
              ElevatedButton.icon(
                onPressed: _isPicking ? null : _captureFromCamera,
                icon: _pickIcon(_PickSource.camera),
                label: Text(_pickLabel(
                  source: _PickSource.camera,
                  idle: 'Fotograf Cek',
                  loading: 'Kamera aciliyor...',
                )),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: _isPicking ? null : _pickFromGallery,
                icon: _pickIcon(_PickSource.gallery),
                label: Text(_pickLabel(
                  source: _PickSource.gallery,
                  idle: 'Galeriden Sec',
                  loading: 'Galeri aciliyor...',
                )),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _pickIcon(_PickSource source) {
    if (_isPicking && _activePickSource == source) {
      return const SizedBox(
        width: 20,
        height: 20,
        child: CircularProgressIndicator(strokeWidth: 2),
      );
    }

    return Icon(
      source == _PickSource.camera
          ? Icons.photo_camera_outlined
          : Icons.photo_library_outlined,
    );
  }

  String _pickLabel({
    required _PickSource source,
    required String idle,
    required String loading,
  }) {
    if (_isPicking && _activePickSource == source) {
      return loading;
    }
    return idle;
  }

  String _basename(String path) {
    final parts = path.split(Platform.pathSeparator);
    return parts.isEmpty ? path : parts.last;
  }
}

enum _PickSource { camera, gallery }
