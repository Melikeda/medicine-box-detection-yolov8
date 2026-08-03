import 'package:flutter/material.dart';

import '../models/analyze_response.dart';
import '../screens/home_screen.dart';
import '../screens/image_preview_screen.dart';
import '../screens/result_screen.dart';
import '../screens/splash_screen.dart';

class ResultRouteArgs {
  const ResultRouteArgs({
    required this.response,
    this.imagePath,
  });

  final AnalyzeResponse response;
  final String? imagePath;
}

class AppRoutes {
  AppRoutes._();

  static const splash = '/';
  static const home = '/home';
  static const imagePreview = '/preview';
  static const result = '/result';

  static Route<dynamic> onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case splash:
        return MaterialPageRoute<void>(
          settings: settings,
          builder: (_) => const SplashScreen(),
        );
      case home:
        return MaterialPageRoute<void>(
          settings: settings,
          builder: (_) => const HomeScreen(),
        );
      case imagePreview:
        final imagePath = settings.arguments as String?;
        if (imagePath == null || imagePath.isEmpty) {
          return MaterialPageRoute<void>(
            settings: settings,
            builder: (_) => const HomeScreen(),
          );
        }
        return MaterialPageRoute<void>(
          settings: settings,
          builder: (_) => ImagePreviewScreen(imagePath: imagePath),
        );
      case result:
        final args = settings.arguments;
        if (args is! ResultRouteArgs) {
          return MaterialPageRoute<void>(
            settings: settings,
            builder: (_) => const HomeScreen(),
          );
        }
        return MaterialPageRoute<void>(
          settings: settings,
          builder: (_) => ResultScreen(
            response: args.response,
            imagePath: args.imagePath,
          ),
        );
      default:
        return MaterialPageRoute<void>(
          settings: settings,
          builder: (_) => const SplashScreen(),
        );
    }
  }
}
