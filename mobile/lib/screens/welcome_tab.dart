import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../l10n/app_localizations.dart';
import '../theme/app_colors.dart';
import '../widgets/home_reminder_banner.dart';
import '../widgets/language_toggle.dart';
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
                        child: _YolocilinWordmark(short: short),
                      ),
                    ),
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
                          minimumSize: Size.fromHeight(short ? 48 : 52),
                        ),
                        child: Text(s.startScan),
                      ),
                    ),
                    SizedBox(height: short ? 8 : 12),
                  ],
                ),
              ),
              HomeReminderBanner(compact: short),
              const SizedBox(height: 6),
            ],
          ),
        ),
      ),
    );
  }
}

class _YolocilinWordmark extends StatelessWidget {
  const _YolocilinWordmark({required this.short});

  final bool short;

  @override
  Widget build(BuildContext context) {
    final brand = context.s.brandLabel;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          brand,
          textAlign: TextAlign.center,
          style: GoogleFonts.playfairDisplay(
            fontSize: short ? 44 : 52,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.5,
            height: 1.05,
            color: AppColors.darkGreen,
          ),
        ),
        SizedBox(height: short ? 10 : 12),
        Container(
          width: short ? 56 : 68,
          height: 2.5,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(999),
            gradient: LinearGradient(
              colors: [
                AppColors.pastelAqua.withValues(alpha: 0),
                AppColors.teal,
                AppColors.pastelAqua.withValues(alpha: 0),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
