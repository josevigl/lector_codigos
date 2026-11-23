import logging
import threading
import time
from collections import defaultdict, deque

from capture.dxgi_capture import DxgiCapture
from core.deduplicator import Deduplicator
from core.validator import validate_candidate
from recognition.rapid_ocr import RapidOcrRecognizer
from system.browser_action import paste_and_continue
from system.clipboard import copy_text
from system.notifier import notify
from vision.differencing import FrameDifferencer
from vision.preprocessing import prepare_for_ocr

logger = logging.getLogger(__name__)


class DetectorPipeline:
    def __init__(self, config):
        capture_config = config.get("capture", {})
        vision_config = config.get("vision", {})
        recognition_config = config.get("recognition", {})
        validation_config = config.get("validation", {})
        automation_config = config.get("automation", {})
        logging_config = config.get("logging", {})

        self.roi = capture_config.get("roi")
        self.fps = capture_config.get("fps", 60)
        self.differencer = FrameDifferencer(
            vision_config.get("mean_difference_threshold", 3.0)
        )
        self.confidence_threshold = float(
            recognition_config.get("confidence_threshold", 0.75)
        )
        self.upscale = float(recognition_config.get("upscale", 2.0))
        self.deduplicator = Deduplicator(
            validation_config.get("dedup_ttl_seconds", 900)
        )
        self.automation_enabled = automation_config.get("enabled", False)
        self.code_field = automation_config.get("code_field")
        self.continue_button = automation_config.get("continue_button")
        self.page_wait_ms = automation_config.get("page_wait_ms", 250)
        if self.automation_enabled and (
            self.code_field is None or self.continue_button is None
        ):
            raise ValueError(
                "Configura automation.code_field y automation.continue_button."
            )
        if self.automation_enabled:
            for name, point in (
                ("automation.code_field", self.code_field),
                ("automation.continue_button", self.continue_button),
            ):
                if (
                    not isinstance(point, (list, tuple))
                    or len(point) != 2
                    or not all(isinstance(value, int) and value >= 0 for value in point)
                ):
                    raise ValueError("{} debe ser una pareja [x, y].".format(name))
            if (
                not isinstance(self.page_wait_ms, int)
                or self.page_wait_ms < 0
            ):
                raise ValueError("automation.page_wait_ms debe ser un entero no negativo.")
        self.metrics_interval = float(
            logging_config.get("metrics_interval_seconds", 30)
        )
        if self.metrics_interval <= 0:
            raise ValueError("logging.metrics_interval_seconds debe ser positivo.")
        self.recognizer = RapidOcrRecognizer(
            use_text_detection=recognition_config.get("use_text_detection", False),
            use_angle_classifier=recognition_config.get(
                "use_angle_classifier", False
            ),
        )
        self._metrics = defaultdict(lambda: deque(maxlen=10000))
        self._last_metrics_log = time.monotonic()
        self._ocr_runs = 0

    def run(self, stop_event):
        if self.roi is None:
            raise ValueError("Falta configurar capture.roi en config.yaml.")
        logger.info("Detector activo. Deténlo con Ctrl+C.")
        if self.automation_enabled:
            logger.info(
                "Automatización activa: campo=%s, botón Continuar=%s",
                self.code_field,
                self.continue_button,
            )
        else:
            logger.info("Automatización desactivada; los candidatos solo se copian.")
        with DxgiCapture(self.roi, self.fps) as capture:
            while not stop_event.is_set():
                frame, capture_ms = capture.get_frame()
                self._record("frame_read_ms", capture_ms)
                if frame is None:
                    self._maybe_log_metrics()
                    stop_event.wait(0.001)
                    continue

                changed_started = time.perf_counter()
                has_changed = self.differencer.changed(frame)
                self._record("change_ms", (time.perf_counter() - changed_started) * 1000)
                if not has_changed:
                    self._maybe_log_metrics()
                    stop_event.wait(0.001)
                    continue

                self._process_changed_frame(frame)
                self._maybe_log_metrics()

    def _process_changed_frame(self, frame):
        pipeline_started = time.perf_counter()

        started = time.perf_counter()
        image = prepare_for_ocr(frame, self.upscale)
        self._record("preprocess_ms", (time.perf_counter() - started) * 1000)

        started = time.perf_counter()
        recognized = self.recognizer.recognize(image)
        ocr_ms = (time.perf_counter() - started) * 1000
        self._record("ocr_ms", ocr_ms)
        self._ocr_runs += 1

        for text, confidence in recognized:
            started = time.perf_counter()
            candidate = validate_candidate(text, confidence, self.confidence_threshold)
            self._record("validation_ms", (time.perf_counter() - started) * 1000)
            if candidate is None:
                pattern = "".join(
                    "X"
                    if character.isalnum()
                    else "_"
                    if character.isspace()
                    else character
                    if character == "-"
                    else "?"
                    for character in text
                )
                reason = (
                    "confidence"
                    if confidence < self.confidence_threshold
                    else "format"
                )
                logger.info(
                    "OCR candidato rechazado (%s): longitud=%d, patrón=%r, "
                    "confianza=%.3f (mínimo=%.3f)",
                    reason,
                    len(text),
                    pattern,
                    confidence,
                    self.confidence_threshold,
                )
                continue
            if self.deduplicator.is_duplicate(candidate):
                continue

            detected_at = time.time()
            started = time.perf_counter()
            copy_text(candidate)
            clipboard_ms = (time.perf_counter() - started) * 1000
            self._record("clipboard_ms", clipboard_ms)
            if self.automation_enabled:
                started = time.perf_counter()
                paste_and_continue(
                    self.code_field,
                    self.continue_button,
                    self.page_wait_ms,
                )
                self._record("browser_action_ms", (time.perf_counter() - started) * 1000)
            copied_at = time.time()
            pipeline_ms = (time.perf_counter() - pipeline_started) * 1000
            self._record("pipeline_ms", pipeline_ms)
            logger.info(
                "Candidato %s; detectado=%s, terminado=%s, "
                "pipeline_ms=%.2f, confianza=%.3f",
                "pegado y se pulsó Continuar" if self.automation_enabled else "copiado",
                time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(detected_at)),
                time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(copied_at)),
                pipeline_ms,
                confidence,
            )
            notify()

    def _record(self, name, value):
        self._metrics[name].append(value)

    def _maybe_log_metrics(self):
        now = time.monotonic()
        if now - self._last_metrics_log < self.metrics_interval:
            return
        for name, values in self._metrics.items():
            if values:
                ordered = sorted(values)
                logger.info(
                    "%s n=%d p50=%.2fms p95=%.2fms p99=%.2fms",
                    name,
                    len(ordered),
                    self._percentile(ordered, 50),
                    self._percentile(ordered, 95),
                    self._percentile(ordered, 99),
                )
        logger.info("OCR ejecutados: %d", self._ocr_runs)
        self._last_metrics_log = now

    @staticmethod
    def _percentile(ordered_values, percentile):
        index = round((len(ordered_values) - 1) * percentile / 100)
        return ordered_values[index]
