from rapidocr_onnxruntime import RapidOCR


class RapidOcrRecognizer:
    def __init__(self, use_text_detection=False, use_angle_classifier=False):
        self._engine = RapidOCR(
            use_text_det=use_text_detection,
            use_angle_cls=use_angle_classifier,
        )

    def recognize(self, image):
        result, _elapsed = self._engine(image)
        if not result:
            return []

        recognized = []
        for item in result:
            if len(item) >= 3:
                recognized.append((str(item[1]), float(item[2])))
        return recognized
