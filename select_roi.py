import logging

import cv2
import dxcam


def main():
    logging.basicConfig(level=logging.WARNING)
    camera = dxcam.create(output_color="BGR")
    frame = camera.grab()
    if frame is None:
        raise RuntimeError(
            "DXGI no devolvió un frame. Comprueba que el escritorio esté visible."
        )

    left, top, width, height = cv2.selectROI(
        "Selecciona el código completo y pulsa ENTER",
        frame,
        showCrosshair=True,
        fromCenter=False,
    )
    cv2.destroyAllWindows()

    if width <= 0 or height <= 0:
        print("No se seleccionó ninguna región.")
        return

    roi = [int(left), int(top), int(left + width), int(top + height)]
    print("Copia esta ROI en config.yaml (izquierda, arriba, derecha, abajo):")
    print("  roi: {}".format(roi))


if __name__ == "__main__":
    main()
