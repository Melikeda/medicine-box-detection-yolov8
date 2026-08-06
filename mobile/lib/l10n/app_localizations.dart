import 'package:flutter/material.dart';

enum AppLanguage { tr, en }

/// Uygulama dili denetleyicisi.
class LocaleController extends ChangeNotifier {
  AppLanguage _language = AppLanguage.tr;

  AppLanguage get language => _language;

  bool get isTurkish => _language == AppLanguage.tr;

  AppStrings get strings => AppStrings.of(_language);

  void setLanguage(AppLanguage language) {
    if (_language == language) {
      return;
    }
    _language = language;
    notifyListeners();
  }

  void toggle() {
    setLanguage(
      _language == AppLanguage.tr ? AppLanguage.en : AppLanguage.tr,
    );
  }
}

/// InheritedNotifier ile tum agaca dil erisimi.
class LocaleScope extends InheritedNotifier<LocaleController> {
  const LocaleScope({
    super.key,
    required LocaleController controller,
    required super.child,
  }) : super(notifier: controller);

  static LocaleController of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<LocaleScope>();
    assert(scope != null, 'LocaleScope not found');
    return scope!.notifier!;
  }

  static LocaleController? maybeOf(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<LocaleScope>()?.notifier;
  }
}

extension AppLocaleX on BuildContext {
  LocaleController get locale => LocaleScope.of(this);

  AppStrings get s => LocaleScope.of(this).strings;
}

/// TR / EN metin katalogu.
class AppStrings {
  const AppStrings._({
    required this.appName,
    required this.brandLabel,
    required this.welcomeTitle,
    required this.welcomeSubtitle,
    required this.startScan,
    required this.popularMedicines,
    required this.navHome,
    required this.navScan,
    required this.navHistory,
    required this.scanTitle,
    required this.scanSubtitle,
    required this.alignBox,
    required this.takePhoto,
    required this.takePhotoHint,
    required this.pickGallery,
    required this.pickGalleryHint,
    required this.tryCamera,
    required this.tryCameraHint,
    required this.historyTitle,
    required this.historyEmptyTitle,
    required this.historyEmptyBody,
    required this.historyLoadError,
    required this.clearHistory,
    required this.clearHistoryConfirm,
    required this.deleteEntry,
    required this.deleteEntryConfirm,
    required this.cancel,
    required this.delete,
    required this.deleted,
    required this.clearAllTooltip,
    required this.categoryPainkiller,
    required this.categoryAntibiotic,
    required this.categoryCough,
    required this.categoryStomach,
    required this.categoryVitamin,
    required this.analyzeResult,
    required this.summary,
    required this.detected,
    required this.matched,
    required this.notFound,
    required this.notBox,
    required this.detectedBoxes,
    required this.noBoxFound,
    required this.noResult,
    required this.noBoxHint,
    required this.backHome,
    required this.aboutMedicine,
    required this.galleryFailed,
    required this.cameraFailed,
  });

  final String appName;
  final String brandLabel;
  final String welcomeTitle;
  final String welcomeSubtitle;
  final String startScan;
  final String popularMedicines;
  final String navHome;
  final String navScan;
  final String navHistory;
  final String scanTitle;
  final String scanSubtitle;
  final String alignBox;
  final String takePhoto;
  final String takePhotoHint;
  final String pickGallery;
  final String pickGalleryHint;
  final String tryCamera;
  final String tryCameraHint;
  final String historyTitle;
  final String historyEmptyTitle;
  final String historyEmptyBody;
  final String historyLoadError;
  final String clearHistory;
  final String clearHistoryConfirm;
  final String deleteEntry;
  final String deleteEntryConfirm;
  final String cancel;
  final String delete;
  final String deleted;
  final String clearAllTooltip;
  final String categoryPainkiller;
  final String categoryAntibiotic;
  final String categoryCough;
  final String categoryStomach;
  final String categoryVitamin;
  final String analyzeResult;
  final String summary;
  final String detected;
  final String matched;
  final String notFound;
  final String notBox;
  final String detectedBoxes;
  final String noBoxFound;
  final String noResult;
  final String noBoxHint;
  final String backHome;
  final String aboutMedicine;
  final String galleryFailed;
  final String cameraFailed;

  static AppStrings of(AppLanguage language) {
    return language == AppLanguage.en ? _en : _tr;
  }

  String categoryFor(String key) {
    switch (key) {
      case 'painkiller':
        return categoryPainkiller;
      case 'antibiotic':
        return categoryAntibiotic;
      case 'cough':
        return categoryCough;
      case 'stomach':
        return categoryStomach;
      case 'vitamin':
        return categoryVitamin;
      default:
        return key;
    }
  }

  static const _tr = AppStrings._(
    appName: 'Yolocilin',
    brandLabel: 'Yolocilin',
    welcomeTitle: 'Hoş Geldiniz',
    welcomeSubtitle:
        'Yolocilin ile ilaç kutusu tanıma.\nFotoğraf çekin, analiz edin, sonucu görün.',
    startScan: 'Taramaya Başla',
    popularMedicines: 'Popüler ilaçlar',
    navHome: 'Ana Sayfa',
    navScan: 'Tara',
    navHistory: 'Geçmiş',
    scanTitle: 'Hızlı İlaç Tarama',
    scanSubtitle:
        'İlaç kutusu fotoğrafını çekin veya galeriden seçin.',
    alignBox: 'Kutuyu çerçeveye hizalayın',
    takePhoto: 'Fotoğraf Çek',
    takePhotoHint: 'Kamera ile tara',
    pickGallery: 'Galeriden Seç',
    pickGalleryHint: 'Kayıtlı fotoğraflardan seç',
    tryCamera: 'Kamerayı Dene',
    tryCameraHint: 'Canlı önizleme ile kutuyu hizala',
    historyTitle: 'Tarama Geçmişi',
    historyEmptyTitle: 'Henüz kayıt yok',
    historyEmptyBody: 'Yaptığınız taramalar burada listelenir.',
    historyLoadError: 'Geçmiş yüklenemedi',
    clearHistory: 'Geçmişi temizle',
    clearHistoryConfirm: 'Tüm tarama kayıtları silinsin mi?',
    deleteEntry: 'Kaydı sil',
    deleteEntryConfirm: 'Bu tarama kaydı silinsin mi?',
    cancel: 'İptal',
    delete: 'Sil',
    deleted: 'Kayıt silindi',
    clearAllTooltip: 'Tümünü sil',
    categoryPainkiller: 'Ağrı Kesici',
    categoryAntibiotic: 'Antibiyotik',
    categoryCough: 'Öksürük İlacı',
    categoryStomach: 'Mide İlacı',
    categoryVitamin: 'Vitamin',
    analyzeResult: 'Analiz Sonucu',
    summary: 'Özet',
    detected: 'Tespit',
    matched: 'Eşleşti',
    notFound: 'Bulunamadı',
    notBox: 'Kutu değil',
    detectedBoxes: 'Tespit edilen kutular',
    noBoxFound: 'Kutu bulunamadı',
    noResult: 'Sonuç yok',
    noBoxHint: 'Fotoğrafta ilaç kutusu tespit edilemedi.',
    backHome: 'Ana Sayfaya Dön',
    aboutMedicine: 'İlaç hakkında',
    galleryFailed: 'Galeri açılamadı',
    cameraFailed: 'Kamera açılamadı',
  );

  static const _en = AppStrings._(
    appName: 'Yolocilin',
    brandLabel: 'Yolocilin',
    welcomeTitle: 'Welcome',
    welcomeSubtitle:
        'Medicine box recognition with Yolocilin.\nTake a photo, analyze, and see the result.',
    startScan: 'Start Scanning',
    popularMedicines: 'Popular medicines',
    navHome: 'Home',
    navScan: 'Scan',
    navHistory: 'History',
    scanTitle: 'Quick Medicine Scan',
    scanSubtitle: 'Take a photo of a medicine box or choose from gallery.',
    alignBox: 'Align the box in the frame',
    takePhoto: 'Take Photo',
    takePhotoHint: 'Scan with camera',
    pickGallery: 'Choose from Gallery',
    pickGalleryHint: 'Pick from saved photos',
    tryCamera: 'Try Camera',
    tryCameraHint: 'Align the box with live preview',
    historyTitle: 'Scan History',
    historyEmptyTitle: 'No records yet',
    historyEmptyBody: 'Your scans will appear here.',
    historyLoadError: 'Could not load history',
    clearHistory: 'Clear history',
    clearHistoryConfirm: 'Delete all scan records?',
    deleteEntry: 'Delete record',
    deleteEntryConfirm: 'Delete this scan record?',
    cancel: 'Cancel',
    delete: 'Delete',
    deleted: 'Record deleted',
    clearAllTooltip: 'Delete all',
    categoryPainkiller: 'Pain Relief',
    categoryAntibiotic: 'Antibiotic',
    categoryCough: 'Cough Medicine',
    categoryStomach: 'Stomach Medicine',
    categoryVitamin: 'Vitamin',
    analyzeResult: 'Analysis Result',
    summary: 'Summary',
    detected: 'Detected',
    matched: 'Matched',
    notFound: 'Not found',
    notBox: 'Not a box',
    detectedBoxes: 'Detected boxes',
    noBoxFound: 'No box found',
    noResult: 'No result',
    noBoxHint: 'No medicine box was detected in the photo.',
    backHome: 'Back to Home',
    aboutMedicine: 'About the medicine',
    galleryFailed: 'Could not open gallery',
    cameraFailed: 'Could not open camera',
  );
}
