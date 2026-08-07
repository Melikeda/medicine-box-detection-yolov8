import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

enum AppLanguage { tr, en }

/// Uygulama dili denetleyicisi (tercih kalıcı).
class LocaleController extends ChangeNotifier {
  LocaleController({AppLanguage language = AppLanguage.tr})
      : _language = language;

  static const _prefsKey = 'app_language';

  AppLanguage _language;

  AppLanguage get language => _language;

  bool get isTurkish => _language == AppLanguage.tr;

  AppStrings get strings => AppStrings.of(_language);

  Future<void> loadSaved() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_prefsKey);
    if (raw == 'en') {
      _language = AppLanguage.en;
      notifyListeners();
    } else if (raw == 'tr') {
      _language = AppLanguage.tr;
      notifyListeners();
    }
  }

  Future<void> setLanguage(AppLanguage language) async {
    if (_language == language) {
      return;
    }
    _language = language;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _prefsKey,
      language == AppLanguage.en ? 'en' : 'tr',
    );
  }

  Future<void> toggle() async {
    await setLanguage(
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
    required this.navHome,
    required this.navScan,
    required this.navHistory,
    required this.scanTitle,
    required this.scanSubtitle,
    required this.alignBox,
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
    required this.homeWarning,
    required this.splashTagline,
    required this.previewTitle,
    required this.previewHint,
    required this.analyze,
    required this.analyzing,
    required this.chooseAnotherPhoto,
    required this.analyzingOverlay,
    required this.analyzingOverlayHint,
    required this.backendNotReady,
    required this.unexpectedError,
    required this.durationLabel,
    required this.boxLabel,
    required this.medicineLabel,
    required this.matchScoreLabel,
    required this.activeIngredientLabel,
    required this.dosageLabel,
    required this.formLabel,
    required this.categoryLabel,
    required this.nearestCandidateLabel,
    required this.ocrLabel,
    required this.statusMatched,
    required this.statusNotFound,
    required this.statusNotBox,
    required this.statusError,
    required this.verifyFromLeaflet,
    required this.explanationFailed,
    required this.retry,
    required this.boxesWord,
    required this.matchedWord,
  });

  final String appName;
  final String brandLabel;
  final String welcomeTitle;
  final String welcomeSubtitle;
  final String startScan;
  final String navHome;
  final String navScan;
  final String navHistory;
  final String scanTitle;
  final String scanSubtitle;
  final String alignBox;
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
  final String homeWarning;
  final String splashTagline;
  final String previewTitle;
  final String previewHint;
  final String analyze;
  final String analyzing;
  final String chooseAnotherPhoto;
  final String analyzingOverlay;
  final String analyzingOverlayHint;
  final String backendNotReady;
  final String unexpectedError;
  final String durationLabel;
  final String boxLabel;
  final String medicineLabel;
  final String matchScoreLabel;
  final String activeIngredientLabel;
  final String dosageLabel;
  final String formLabel;
  final String categoryLabel;
  final String nearestCandidateLabel;
  final String ocrLabel;
  final String statusMatched;
  final String statusNotFound;
  final String statusNotBox;
  final String statusError;
  final String verifyFromLeaflet;
  final String explanationFailed;
  final String retry;
  final String boxesWord;
  final String matchedWord;

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

  String boxLabelFor(int boxIndex) => '$boxLabel $boxIndex';

  String historySubtitle({
    required int detectionCount,
    required int matchedCount,
    required DateTime createdAt,
  }) {
    final date =
        '${createdAt.day.toString().padLeft(2, '0')}.'
        '${createdAt.month.toString().padLeft(2, '0')}.'
        '${createdAt.year} '
        '${createdAt.hour.toString().padLeft(2, '0')}:'
        '${createdAt.minute.toString().padLeft(2, '0')}';
    return '$detectionCount $boxesWord · $matchedCount $matchedWord · $date';
  }

  String durationLine({
    required double seconds,
    required String ocrMode,
  }) {
    return '$durationLabel: ${seconds.toStringAsFixed(1)} · OCR: $ocrMode';
  }

  String unexpectedErrorWith(Object error) => '$unexpectedError: $error';

  static const _tr = AppStrings._(
    appName: 'Yolocilin',
    brandLabel: 'Yolocilin',
    welcomeTitle: 'Hoş Geldiniz',
    welcomeSubtitle:
        'Yolocilin ile ilaç kutusu tanıma.\nFotoğraf çekin, analiz edin, sonucu görün.',
    startScan: 'Taramaya Başla',
    navHome: 'Ana Sayfa',
    navScan: 'Tara',
    navHistory: 'Geçmiş',
    scanTitle: 'Hızlı İlaç Tarama',
    scanSubtitle: 'İlaç kutusu fotoğrafını çekin veya galeriden seçin.',
    alignBox: 'Kutuyu çerçeveye hizalayın',
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
    homeWarning:
        'Uyarı: Bu uygulama tıbbi tavsiye yerine geçmez. İlaç kullanımı için doktorunuza veya eczacınıza danışın.',
    splashTagline: 'İlaç Kutusu Tanıma',
    previewTitle: 'Önizleme',
    previewHint: 'Analiz, YOLO tespiti ve OCR ile ilaç kutularını tanır.',
    analyze: 'Analiz Et',
    analyzing: 'Analiz ediliyor...',
    chooseAnotherPhoto: 'Başka fotoğraf seç',
    analyzingOverlay: 'İlaç kutusu analiz ediliyor...',
    analyzingOverlayHint: 'CPU üzerinde OCR 1-3 dakika sürebilir (fast mod).',
    backendNotReady:
        'Backend hazır değil veya modeller yüklenmedi.\nÖnce python run_api.py çalıştırın.',
    unexpectedError: 'Beklenmeyen hata',
    durationLabel: 'Süre',
    boxLabel: 'Kutu',
    medicineLabel: 'İlaç',
    matchScoreLabel: 'Eşleşme skoru',
    activeIngredientLabel: 'Etken madde',
    dosageLabel: 'Doz',
    formLabel: 'Form',
    categoryLabel: 'Kategori',
    nearestCandidateLabel: 'En yakın aday',
    ocrLabel: 'OCR',
    statusMatched: 'Eşleşti',
    statusNotFound: 'Bulunamadı',
    statusNotBox: 'Kutu değil',
    statusError: 'Hata',
    verifyFromLeaflet: 'Resmi ürün bilgisinden doğrulanmalı',
    explanationFailed: 'Açıklama yüklenemedi.',
    retry: 'Tekrar dene',
    boxesWord: 'kutu',
    matchedWord: 'eşleşti',
  );

  static const _en = AppStrings._(
    appName: 'Yolocilin',
    brandLabel: 'Yolocilin',
    welcomeTitle: 'Welcome',
    welcomeSubtitle:
        'Medicine box recognition with Yolocilin.\nTake a photo, analyze, and see the result.',
    startScan: 'Start Scanning',
    navHome: 'Home',
    navScan: 'Scan',
    navHistory: 'History',
    scanTitle: 'Quick Medicine Scan',
    scanSubtitle: 'Take a photo of a medicine box or choose from gallery.',
    alignBox: 'Align the box in the frame',
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
    homeWarning:
        'Warning: This app does not replace medical advice. Consult your doctor or pharmacist before using any medicine.',
    splashTagline: 'Medicine Box Recognition',
    previewTitle: 'Preview',
    previewHint: 'Analysis recognizes medicine boxes with YOLO and OCR.',
    analyze: 'Analyze',
    analyzing: 'Analyzing...',
    chooseAnotherPhoto: 'Choose another photo',
    analyzingOverlay: 'Analyzing medicine box...',
    analyzingOverlayHint: 'OCR on CPU may take 1-3 minutes (fast mode).',
    backendNotReady:
        'Backend is not ready or models are not loaded.\nStart it with python run_api.py first.',
    unexpectedError: 'Unexpected error',
    durationLabel: 'Time',
    boxLabel: 'Box',
    medicineLabel: 'Medicine',
    matchScoreLabel: 'Match score',
    activeIngredientLabel: 'Active ingredient',
    dosageLabel: 'Dose',
    formLabel: 'Form',
    categoryLabel: 'Category',
    nearestCandidateLabel: 'Closest candidate',
    ocrLabel: 'OCR',
    statusMatched: 'Matched',
    statusNotFound: 'Not found',
    statusNotBox: 'Not a box',
    statusError: 'Error',
    verifyFromLeaflet: 'Must be verified from the official leaflet',
    explanationFailed: 'Could not load explanation.',
    retry: 'Try again',
    boxesWord: 'boxes',
    matchedWord: 'matched',
  );
}
