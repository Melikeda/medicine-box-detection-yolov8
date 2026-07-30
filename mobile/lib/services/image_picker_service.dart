import 'package:image_picker/image_picker.dart';

/// Galeri erisimi icin ince bir servis katmani.
class ImagePickerService {
  ImagePickerService({ImagePicker? picker}) : _picker = picker ?? ImagePicker();

  final ImagePicker _picker;

  Future<String?> pickFromGallery() async {
    final file = await _picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 85,
    );
    return file?.path;
  }
}
