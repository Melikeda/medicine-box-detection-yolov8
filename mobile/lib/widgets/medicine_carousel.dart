import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../l10n/app_localizations.dart';
import '../theme/app_colors.dart';

class FeaturedMedicine {
  const FeaturedMedicine({
    required this.name,
    required this.categoryKey,
    required this.gradient,
    required this.imageUrl,
    required this.icon,
  });

  final String name;
  final String categoryKey;
  final List<Color> gradient;
  final String imageUrl;
  final IconData icon;
}

const featuredMedicines = <FeaturedMedicine>[
  FeaturedMedicine(
    name: 'Parol',
    categoryKey: 'painkiller',
    gradient: [Color(0xFF38BDF8), Color(0xFF0EA5E9)],
    icon: Icons.medication_outlined,
    imageUrl:
        'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=640&q=80',
  ),
  FeaturedMedicine(
    name: 'Nurofen',
    categoryKey: 'painkiller',
    gradient: [Color(0xFF2DD4BF), Color(0xFF14B8A6)],
    icon: Icons.medical_services_outlined,
    imageUrl:
        'https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=640&q=80',
  ),
  FeaturedMedicine(
    name: 'Augmentin',
    categoryKey: 'antibiotic',
    gradient: [Color(0xFF60A5FA), Color(0xFF3B82F6)],
    icon: Icons.vaccines_outlined,
    imageUrl:
        'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=640&q=80',
  ),
  FeaturedMedicine(
    name: 'Mucosolvan',
    categoryKey: 'cough',
    gradient: [Color(0xFF34D399), Color(0xFF10B981)],
    icon: Icons.healing_outlined,
    imageUrl:
        'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=640&q=80',
  ),
  FeaturedMedicine(
    name: 'Omesek',
    categoryKey: 'stomach',
    gradient: [Color(0xFF7DD3FC), Color(0xFF0284C7)],
    icon: Icons.local_pharmacy_outlined,
    imageUrl:
        'https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?auto=format&fit=crop&w=640&q=80',
  ),
  FeaturedMedicine(
    name: 'Redoxon',
    categoryKey: 'vitamin',
    gradient: [Color(0xFFFBBF24), Color(0xFFF59E0B)],
    icon: Icons.eco_outlined,
    imageUrl:
        'https://images.unsplash.com/photo-1576602976047-174e57a47881?auto=format&fit=crop&w=640&q=80',
  ),
];

class MedicineCarousel extends StatelessWidget {
  const MedicineCarousel({super.key, this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    final s = context.s;
    final listHeight = compact ? 148.0 : 168.0;
    final cardWidth = compact ? 128.0 : 140.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          s.popularMedicines,
          style: GoogleFonts.poppins(
            fontSize: compact ? 15 : 16,
            fontWeight: FontWeight.w700,
            color: AppColors.primary,
          ),
        ),
        SizedBox(height: compact ? 8 : 10),
        SizedBox(
          height: listHeight,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            padding: EdgeInsets.zero,
            itemCount: featuredMedicines.length,
            separatorBuilder: (_, __) => const SizedBox(width: 10),
            itemBuilder: (context, index) {
              return _MedicineCarouselCard(
                medicine: featuredMedicines[index],
                width: cardWidth,
                compact: compact,
              );
            },
          ),
        ),
      ],
    );
  }
}

class _MedicineCarouselCard extends StatelessWidget {
  const _MedicineCarouselCard({
    required this.medicine,
    required this.width,
    required this.compact,
  });

  final FeaturedMedicine medicine;
  final double width;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final category = context.s.categoryFor(medicine.categoryKey);

    return Container(
      width: width,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.divider),
        boxShadow: [
          BoxShadow(
            color: medicine.gradient.last.withValues(alpha: 0.16),
            blurRadius: 12,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            flex: 6,
            child: Stack(
              fit: StackFit.expand,
              children: [
                DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: medicine.gradient,
                    ),
                  ),
                ),
                Image.network(
                  medicine.imageUrl,
                  fit: BoxFit.cover,
                  loadingBuilder: (context, child, progress) {
                    if (progress == null) {
                      return child;
                    }
                    return Center(
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white.withValues(alpha: 0.9),
                          value: progress.expectedTotalBytes != null
                              ? progress.cumulativeBytesLoaded /
                                  progress.expectedTotalBytes!
                              : null,
                        ),
                      ),
                    );
                  },
                  errorBuilder: (_, __, ___) {
                    return Center(
                      child: Icon(
                        medicine.icon,
                        size: compact ? 36 : 42,
                        color: Colors.white.withValues(alpha: 0.9),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
          Expanded(
            flex: 4,
            child: Padding(
              padding: EdgeInsets.fromLTRB(
                compact ? 10 : 12,
                compact ? 8 : 10,
                compact ? 10 : 12,
                compact ? 8 : 10,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    medicine.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: GoogleFonts.poppins(
                      color: AppColors.primary,
                      fontSize: compact ? 13 : 14,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    category,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: GoogleFonts.poppins(
                      color: AppColors.textSecondary,
                      fontSize: compact ? 10 : 11,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
