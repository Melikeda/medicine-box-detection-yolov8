import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../l10n/app_localizations.dart';
import '../widgets/animated_yolocilin_hero_3d.dart';
import '../widgets/language_toggle.dart';
import '../widgets/medicine_carousel.dart';
import '../widgets/professional_background.dart';

/// Ana giriş sayfası — kaydırmasız tam ekran düzeni.
class WelcomeTab extends StatelessWidget {
  const WelcomeTab({super.key, required this.onStartScan});

  final VoidCallback onStartScan;

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    final short = size.height < 740;
    final s = context.s;

    return ProfessionalBackground(
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Align(
                alignment: Alignment.centerRight,
                child: LanguageToggle(),
              ),
              Expanded(
                flex: short ? 11 : 12,
                child: Column(
                  children: [
                    Expanded(
                      child: Center(
                        child: LayoutBuilder(
                          builder: (context, constraints) {
                            final heroScale = (constraints.maxHeight / 240)
                                .clamp(0.62, short ? 0.88 : 1.0);
                            return AnimatedYolocilinHero3D(scale: heroScale);
                          },
                        ),
                      ),
                    ),
                    Text(
                      s.brandLabel,
                      textAlign: TextAlign.center,
                      style: GoogleFonts.poppins(
                        fontSize: short ? 13 : 14,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 1.1,
                        color: const Color(0xFF2D6A4F),
                      ),
                    ),
                    SizedBox(height: short ? 4 : 6),
                    Text(
                      s.welcomeTitle,
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                            fontSize: short ? 24 : 28,
                          ),
                    ),
                    SizedBox(height: short ? 6 : 8),
                    Text(
                      s.welcomeSubtitle,
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            height: 1.35,
                            fontSize: short ? 13 : 14,
                          ),
                    ),
                    SizedBox(height: short ? 12 : 16),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: onStartScan,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2D6A4F),
                          foregroundColor: Colors.white,
                          minimumSize: Size.fromHeight(short ? 48 : 52),
                        ),
                        child: Text(s.startScan),
                      ),
                    ),
                    SizedBox(height: short ? 8 : 12),
                  ],
                ),
              ),
              MedicineCarousel(compact: short),
              const SizedBox(height: 6),
            ],
          ),
        ),
      ),
    );
  }
}
