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

  Future<void> _pickImage() async {
    setState(() => _isPicking = true);

    try {
      final path = await _imagePickerService.pickFromGallery();
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
      _showError('Galeri acilamadi: $error');
    } finally {
      if (mounted) {
        setState(() => _isPicking = false);
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
                        Icons.photo_library_outlined,
                        size: 56,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Ilac kutusu fotografi secin',
                        textAlign: TextAlign.center,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Galeriden bir fotograf secerek onizleme ekranina gecin. '
                        'API analizi bir sonraki asamada eklenecek.',
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
                onPressed: _isPicking ? null : _pickImage,
                icon: _isPicking
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.photo_library),
                label: Text(
                  _isPicking ? 'Galeri aciliyor...' : 'Galeriden Sec',
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _basename(String path) {
    final parts = path.split(Platform.pathSeparator);
    return parts.isEmpty ? path : parts.last;
  }
}
