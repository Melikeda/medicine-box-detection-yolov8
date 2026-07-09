# 🤖 YOLOv8 Training Report

## 📌 Purpose

The purpose of this phase is to train a YOLOv8 object detection model using the prepared medicine box dataset and evaluate its performance on unseen images.

This phase includes model training, performance evaluation, and prediction using the best trained model.

---

# 🎯 Objectives

- Train the YOLOv8n model
- Configure training parameters
- Evaluate model performance
- Analyze training metrics
- Generate the best trained model
- Perform prediction on test images
- Evaluate prediction results

---

# 🧠 Model Configuration

The project uses the **YOLOv8 Nano (YOLOv8n)** model provided by Ultralytics.

The model was initialized using pretrained weights to apply **Transfer Learning**, allowing the network to learn medicine box detection more efficiently.

Model used:

```text
yolov8n.pt
```

---

# ⚙️ Training Configuration

The following training parameters were used:

| Parameter | Value |
|-----------|-------|
| Model | YOLOv8n |
| Epochs | 50 |
| Image Size | 640 × 640 |
| Batch Size | 8 |
| Device | CPU |
| Dataset | Roboflow YOLOv8 Dataset |

---

# 📄 Training Script

The training process was implemented in **src/train.py**.

Main training configuration:

```python
model = YOLO("yolov8n.pt")

model.train(
    data="data/dataset/data.yaml",
    epochs=50,
    imgsz=640,
    batch=8,
    device="cpu",
    project="runs/detect",
    name="medicine_box_yolov8n"
)
```

The model automatically loads the pretrained YOLOv8n weights and starts training using the prepared dataset.

---

# 📊 Training Outputs

After training, YOLOv8 generated several output files including:

```text
best.pt
last.pt
results.csv
confusion_matrix.png
F1_curve.png
P_curve.png
R_curve.png
PR_curve.png
```

These files were used to evaluate the training process and model performance.

---

# 📈 Training Evaluation

The trained model achieved stable learning during the training process.

The evaluation metrics indicated that:

- Precision increased throughout training.
- Recall remained stable.
- mAP values improved over epochs.
- Training and validation losses decreased consistently.

Overall, the model successfully learned to detect medicine boxes with satisfactory performance.

---

# 🔍 Prediction

After training, the generated **best.pt** model was used to perform prediction on the test dataset.

Prediction was implemented in:

```text
src/predict.py
```

The prediction process:

```text
Test Images
      │
      ▼
Load best.pt
      │
      ▼
YOLOv8 Prediction
      │
      ▼
Bounding Box Detection
      │
      ▼
Prediction Results
```

Prediction results were automatically saved inside the project output directory.

---

# 📊 Prediction Evaluation

The trained model successfully detected medicine boxes in most test images.

Observed results:

- High confidence scores (generally between **0.80–0.93**)
- Accurate detection on single-object images
- Successful detection of multiple medicine boxes
- Good performance on different viewing angles

Some medicine boxes were not detected under challenging conditions such as:

- Low-light environments
- Partially visible objects

These cases suggest that increasing dataset diversity could further improve model performance.

---

# 📌 Outcome

At the end of this phase:

- YOLOv8n model was successfully trained.
- The best performing model (**best.pt**) was generated.
- Training metrics were analyzed.
- Prediction was successfully performed on the test dataset.
- Prediction results confirmed that the model can reliably detect medicine boxes under normal conditions.

The project is now ready for the image preprocessing stage.

---

# 📍 Next Phase

The next development stage is:

```text
feature/opencv-preprocessing
```

This phase will focus on cropping detected medicine boxes, improving image quality using OpenCV, and preparing images for OCR.