import logging
import time

import dxcam

logger = logging.getLogger(__name__)


class DxgiCapture:
    def __init__(self, roi, fps):
        if len(roi) != 4:
            raise ValueError("capture.roi debe tener cuatro coordenadas.")
        left, top, right, bottom = roi
        if not all(isinstance(value, int) for value in roi):
            raise ValueError("Las coordenadas de capture.roi deben ser enteros.")
        if left < 0 or top < 0 or right <= left or bottom <= top:
            raise ValueError("capture.roi no es una región válida.")
        if not isinstance(fps, int) or fps < 1:
            raise ValueError("capture.fps debe ser un entero positivo.")

        self.roi = tuple(roi)
        self.fps = fps
        self._camera = None

    def __enter__(self):
        self._camera = dxcam.create(output_color="BGR")
        self._camera.start(target_fps=self.fps, region=self.roi)
        logger.info("Captura DXGI iniciada; ROI=%s, fps=%s", self.roi, self.fps)
        width = self.roi[2] - self.roi[0]
        height = self.roi[3] - self.roi[1]
        if width < 120 or height < 20:
            logger.warning(
                "La ROI mide solo %dx%d píxeles. Amplíala para incluir el código "
                "completo, con margen alrededor; una ROI tan pequeña suele "
                "dificultar el OCR.",
                width,
                height,
            )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._camera is not None:
            self._camera.stop()
            self._camera = None

    def get_frame(self):
        if self._camera is None:
            raise RuntimeError("La captura DXGI no está iniciada.")
        started = time.perf_counter()
        frame = self._camera.get_latest_frame()
        frame_read_ms = (time.perf_counter() - started) * 1000
        return frame, frame_read_ms
