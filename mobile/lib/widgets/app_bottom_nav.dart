import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../l10n/app_localizations.dart';
import '../theme/app_colors.dart';

/// Tam genislik standart alt navigasyon (telefon cercevesine oturur).
class AppBottomNav extends StatelessWidget {
  const AppBottomNav({
    super.key,
    required this.currentIndex,
    required this.onTabSelected,
  });

  final int currentIndex;
  final ValueChanged<int> onTabSelected;

  @override
  Widget build(BuildContext context) {
    final s = context.s;
    final bottomInset = MediaQuery.paddingOf(context).bottom;
    final tabs = [
      _NavTab(icon: Icons.home_rounded, label: s.navHome),
      _NavTab(icon: Icons.qr_code_scanner_rounded, label: s.navScan),
      _NavTab(icon: Icons.history_rounded, label: s.navHistory),
    ];

    return Material(
      color: Colors.white,
      elevation: 8,
      shadowColor: AppColors.teal.withValues(alpha: 0.18),
      child: Container(
        width: double.infinity,
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(color: AppColors.divider, width: 1),
          ),
        ),
        padding: EdgeInsets.fromLTRB(4, 6, 4, 6 + bottomInset),
        child: Row(
          children: [
            for (var i = 0; i < tabs.length; i++)
              Expanded(
                child: _NavItem(
                  tab: tabs[i],
                  selected: currentIndex == i,
                  onTap: () => onTabSelected(i),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _NavTab {
  const _NavTab({required this.icon, required this.label});

  final IconData icon;
  final String label;
}

class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.tab,
    required this.selected,
    required this.onTap,
  });

  final _NavTab tab;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = selected ? AppColors.navActive : AppColors.textSecondary;

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              width: 42,
              height: 32,
              decoration: BoxDecoration(
                color: selected
                    ? AppColors.navActive.withValues(alpha: 0.14)
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(tab.icon, size: 24, color: color),
            ),
            const SizedBox(height: 2),
            Text(
              tab.label,
              style: GoogleFonts.poppins(
                fontSize: 11,
                fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
