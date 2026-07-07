from argparse import ArgumentParser
from pathlib import Path
from PIL import Image, ImageDraw


DEFAULT_CLASS_NAMES = {
    0: "medicine-box",
}


def yolo_to_pixel_coordinates(
    x_center: float,
    y_center: float,
    box_width: float,
    box_height: float,
    image_width: int,
    image_height: int,
) -> tuple[int, int, int, int]:
    """
    Converts YOLO normalized bounding box coordinates to pixel coordinates.
    """

    x_center *= image_width
    y_center *= image_height
    box_width *= image_width
    box_height *= image_height

    x1 = int(x_center - box_width / 2)
    y1 = int(y_center - box_height / 2)
    x2 = int(x_center + box_width / 2)
    y2 = int(y_center + box_height / 2)

    return x1, y1, x2, y2


def visualize_yolo_label(
    image_path: Path,
    label_path: Path,
    output_path: Path,
    class_names: dict[int, str] | None = None,
) -> None:
    """
    Draws YOLO bounding boxes on an image and saves the result.
    """

    if class_names is None:
        class_names = DEFAULT_CLASS_NAMES

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if not label_path.exists():
        raise FileNotFoundError(f"Label file not found: {label_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.open(image_path).convert("RGB")
    image_width, image_height = image.size
    draw = ImageDraw.Draw(image)

    with open(label_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    box_count = 0

    for line in lines:
        values = line.strip().split()

        if len(values) != 5:
            continue

        class_id = int(float(values[0]))
        x_center = float(values[1])
        y_center = float(values[2])
        box_width = float(values[3])
        box_height = float(values[4])

        x1, y1, x2, y2 = yolo_to_pixel_coordinates(
            x_center=x_center,
            y_center=y_center,
            box_width=box_width,
            box_height=box_height,
            image_width=image_width,
            image_height=image_height,
        )

        label = class_names.get(class_id, f"class-{class_id}")

        draw.rectangle([x1, y1, x2, y2], outline="green", width=4)
        draw.text((x1, max(y1 - 20, 0)), label, fill="green")

        box_count += 1

    image.save(output_path)

    print("\nYOLO Label Visualization")
    print("------------------------")
    print(f"Image : {image_path}")
    print(f"Label : {label_path}")
    print(f"Output: {output_path}")
    print(f"Boxes : {box_count}")
    print("Status: Success")


def parse_arguments():
    parser = ArgumentParser(
        description="Visualize YOLO label files by drawing bounding boxes on images."
    )

    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Path to the input image file.",
    )

    parser.add_argument(
        "--label",
        type=Path,
        required=True,
        help="Path to the YOLO label file.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/images/label_visualization.jpg"),
        help="Path to save the output visualization image.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    visualize_yolo_label(
        image_path=args.image,
        label_path=args.label,
        output_path=args.output,
    )