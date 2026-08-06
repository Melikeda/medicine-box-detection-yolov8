import 'package:flutter/material.dart';

import '../routes/app_router.dart';
import '../services/image_picker_service.dart';
import '../l10n/app_localizations.dart';
import '../widgets/app_bottom_nav.dart';
import 'history_screen.dart';
import 'scan_tab.dart';
import 'welcome_tab.dart';

export 'scan_tab.dart' show PickSource;

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key, this.initialTab = 0});

  final int initialTab;

  @override
  Widget build(BuildContext context) {
    return MainShellScreen(initialIndex: initialTab);
  }
}

class MainShellScreen extends StatefulWidget {
  const MainShellScreen({super.key, this.initialIndex = 0});

  final int initialIndex;

  @override
  State<MainShellScreen> createState() => _MainShellScreenState();
}

class _MainShellScreenState extends State<MainShellScreen> {
  final ImagePickerService _imagePickerService = ImagePickerService();
  final GlobalKey<HistoryScreenState> _historyKey = GlobalKey();

  late int _currentIndex;
  bool _isPicking = false;
  PickSource? _activePickSource;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex.clamp(0, 2);
  }

  void _onTabSelected(int index) {
    setState(() => _currentIndex = index);
    if (index == 2) {
      _historyKey.currentState?.reload();
    }
  }

  Future<void> _pickFromGallery() {
    return _pickImage(
      source: PickSource.gallery,
      picker: _imagePickerService.pickFromGallery,
      failureMessage: context.s.galleryFailed,
    );
  }

  Future<void> _captureFromCamera() {
    return _pickImage(
      source: PickSource.camera,
      picker: _imagePickerService.pickFromCamera,
      failureMessage: context.s.cameraFailed,
    );
  }

  Future<void> _pickImage({
    required PickSource source,
    required Future<String?> Function() picker,
    required String failureMessage,
  }) async {
    setState(() {
      _isPicking = true;
      _activePickSource = source;
    });

    try {
      final path = await picker();
      if (!mounted || path == null) {
        return;
      }

      await Navigator.of(context).pushNamed(
        AppRoutes.imagePreview,
        arguments: path,
      );
      _historyKey.currentState?.reload();
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
    return Scaffold(
      backgroundColor: Colors.transparent,
      resizeToAvoidBottomInset: true,
      body: IndexedStack(
        index: _currentIndex,
        children: [
          WelcomeTab(
            onStartScan: () => _onTabSelected(1),
          ),
          ScanTab(
            onCameraTap: _captureFromCamera,
            onGalleryTap: _pickFromGallery,
            isPicking: _isPicking,
            activePickSource: _activePickSource,
          ),
          HistoryScreen(
            key: _historyKey,
            embedded: true,
            onEntryOpened: () => _historyKey.currentState?.reload(),
          ),
        ],
      ),
      bottomNavigationBar: AppBottomNav(
        currentIndex: _currentIndex,
        onTabSelected: _onTabSelected,
      ),
    );
  }
}
