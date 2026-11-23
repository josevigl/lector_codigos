import cv2


def prepare_for_ocr(frame, upscale):
    if upscale < 1:
        raise ValueError("recognition.upscale debe ser al menos 1.")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    if upscale != 1:
        gray = cv2.resize(
            gray,
            None,
            fx=upscale,
            fy=upscale,
            interpolation=cv2.INTER_CUBIC,
        )
    return gray
