import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/config/app_config.dart';
import 'package:medicine_box_app/screens/home_screen.dart';

void main() {
  testWidgets('Home screen shows camera and gallery actions', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(),
      ),
    );

    expect(find.text(AppConfig.appName), findsOneWidget);
    expect(find.text('Fotograf Cek'), findsOneWidget);
    expect(find.text('Galeriden Sec'), findsOneWidget);
    expect(find.byIcon(Icons.photo_camera_outlined), findsOneWidget);
    expect(find.byIcon(Icons.photo_library_outlined), findsOneWidget);
  });
}
