import 'package:flutter/material.dart';

import 'config/app_config.dart';
import 'routes/app_router.dart';
import 'theme/app_theme.dart';

class MedicineBoxApp extends StatelessWidget {
  const MedicineBoxApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConfig.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      initialRoute: AppRoutes.splash,
      onGenerateRoute: AppRoutes.onGenerateRoute,
    );
  }
}
