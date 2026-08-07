import 'package:flutter/material.dart';

import 'config/app_config.dart';
import 'l10n/app_localizations.dart';
import 'routes/app_router.dart';
import 'theme/app_theme.dart';

class MedicineBoxApp extends StatefulWidget {
  const MedicineBoxApp({super.key});

  @override
  State<MedicineBoxApp> createState() => _MedicineBoxAppState();
}

class _MedicineBoxAppState extends State<MedicineBoxApp> {
  final LocaleController _localeController = LocaleController();

  @override
  void initState() {
    super.initState();
    _localeController.loadSaved();
  }

  @override
  void dispose() {
    _localeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LocaleScope(
      controller: _localeController,
      child: ListenableBuilder(
        listenable: _localeController,
        builder: (context, _) {
          final s = _localeController.strings;
          return MaterialApp(
            title: s.appName.isEmpty ? AppConfig.appName : s.appName,
            debugShowCheckedModeBanner: false,
            theme: AppTheme.light,
            locale: _localeController.isTurkish
                ? const Locale('tr')
                : const Locale('en'),
            initialRoute: AppRoutes.splash,
            onGenerateRoute: AppRoutes.onGenerateRoute,
          );
        },
      ),
    );
  }
}
