from paddleocr import PaddleOCR


def create_paddle_ocr_reader() -> PaddleOCR:
    """
    CPU üzerinde çalışan PaddleOCR okuyucusunu oluşturur.

    oneDNN/MKLDNN kapatılmıştır çünkü PaddlePaddle 3.3.x
    sürümünde Windows CPU çıkarımında uyumluluk hatası
    oluşabilmektedir.
    """
    reader = PaddleOCR(
        lang="en",
        device="cpu",
        enable_mkldnn=False,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    return reader