from ultralytics import YOLO #Ultralytics kütüphanesindeki YOLO sınıfını kullanmak


def train_model():
    # YOLOv8n modelini yükler.
    # Eğer yolov8n.pt bilgisayarda yoksa otomatik indirir.
    model = YOLO("yolov8n.pt")

    # Modeli kendi Roboflow veri setimizle eğitir. Burada eğitim başlıyor
    model.train(
        data="data/dataset/data.yaml",
        epochs=50,
        imgsz=640,
        batch=8,
        device="cpu",
        project="runs/detect",
        name="medicine_box_yolov8n"
    )


if __name__ == "__main__":
    train_model()