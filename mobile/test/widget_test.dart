import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_box_app/app.dart';
import 'package:medicine_box_app/config/app_config.dart';

void main() {
  testWidgets('Splash screen shows app title', (tester) async {
    await tester.pumpWidget(const MedicineBoxApp());
    await tester.pump();

    expect(find.text(AppConfig.appName), findsOneWidget);
  });
}
