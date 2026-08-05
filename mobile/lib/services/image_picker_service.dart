import 'package:image_picker/image_picker.dart';

/// Galeri ve kamera erisimi icin ince servis katmani.
class ImagePickerService {
  ImagePickerService({ImagePicker? picker}) : _picker = picker ?? ImagePicker();

  final ImagePicker _picker;

  Future<String?> pickFromGallery() {
    return _pickImage(source: ImageSource.gallery);
  }

  Future<String?> pickFromCamera() {
    return _pickImage(source: ImageSource.camera);
  }

  Future<String?> _pickImage({required ImageSource source}) async {
    final file = await _picker.pickImage(
      source: source,
      imageQuality: 65,
      maxWidth: 1280,
      maxHeight: 1280,
      preferredCameraDevice: CameraDevice.rear,
    );
    return file?.path;
  }
}
