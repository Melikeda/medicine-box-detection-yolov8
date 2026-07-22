from pathlib import Path

from src.ocr.experimental.paddle_ocr_reader import (
    create_paddle_ocr_reader,
)


def print_ocr_results(
    texts: list[str],
    scores: list[float],
) -> None:
    """
    PaddleOCR tarafÄ±ndan bulunan metinleri
    gÃ¼ven skorlarÄ±yla birlikte terminale yazdÄ±rÄ±r.
    """
    print("\nPaddleOCR SonuÃ§larÄ±")
    print("-" * 60)

    if not texts:
        print("Herhangi bir metin bulunamadÄ±.")
        return

    for index, (text, score) in enumerate(
        zip(texts, scores),
        start=1,
    ):
        print(
            f"{index}. {text} "
            f"(GÃ¼ven: {score:.2%})"
        )


def main() -> None:
    """
    A-Ferin Forte gÃ¶rselini PaddleOCR ile okur.
    """
    input_path = Path(
        "data/samples/aferin_forte.jpg"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"GÃ¶rsel bulunamadÄ±: {input_path}"
        )

    reader = create_paddle_ocr_reader()

    print("\nPaddleOCR Ã§alÄ±ÅŸtÄ±rÄ±lÄ±yor...")
    print(f"GÃ¶rsel: {input_path}")

    results = reader.predict(
        input=str(input_path),
    )

    all_texts: list[str] = []
    all_scores: list[float] = []

    for result in results:
        result_data = result.json["res"]

        texts = result_data.get(
            "rec_texts",
            [],
        )

        scores = result_data.get(
            "rec_scores",
            [],
        )

        all_texts.extend(texts)
        all_scores.extend(
            float(score)
            for score in scores
        )

    print_ocr_results(
        texts=all_texts,
        scores=all_scores,
    )


if __name__ == "__main__":
    main()
