import logging
from pathlib import Path

import cv2
import dxcam
import yaml


def save_action_coordinates(config_path, code_field, continue_button):
    config_path = Path(config_path)
    text = config_path.read_text(encoding="utf-8")
    config = yaml.safe_load(text) or {}
    automation = config.get("automation", {})
    page_wait_ms = automation.get("page_wait_ms", 250)

    section = [
        "automation:",
        "  # Coordinates are captured from DXcam output 0.",
        "  enabled: true",
        "  code_field: [{}, {}]".format(*code_field),
        "  continue_button: [{}, {}]".format(*continue_button),
        "  page_wait_ms: {}".format(page_wait_ms),
    ]
    lines = text.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line.startswith("automation:")),
        None,
    )
    if start is None:
        lines.extend([""] if lines and lines[-1] else [])
        lines.extend(section)
    else:
        end = next(
            (
                index
                for index in range(start + 1, len(lines))
                if lines[index]
                and not lines[index][0].isspace()
                and not lines[index].startswith("#")
            ),
            len(lines),
        )
        lines[start:end] = section

    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    logging.basicConfig(level=logging.WARNING)
    frame = dxcam.create(output_color="BGR").grab()
    if frame is None:
        raise RuntimeError(
            "DXGI no devolvió un frame. Comprueba que el escritorio esté visible."
        )

    points = []
    preview = frame.copy()
    window_name = "Selecciona el campo y Continuar (ESC para cancelar)"

    def on_mouse(event, x, y, _flags, _parameter):
        if event != cv2.EVENT_LBUTTONDOWN or len(points) >= 2:
            return
        points.append((int(x), int(y)))
        cv2.circle(preview, points[-1], 8, (0, 255, 0), 2)
        cv2.imshow(window_name, preview)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, on_mouse)
    cv2.imshow(window_name, preview)
    print("Haz clic en el centro del campo del código.")
    print("Después, haz clic en el centro del botón Continuar.")

    while len(points) < 2:
        if cv2.waitKey(20) & 0xFF == 27:
            cv2.destroyAllWindows()
            print("Seleccion cancelada.")
            return

    cv2.destroyAllWindows()
    config_path = Path(__file__).resolve().with_name("config.yaml")
    save_action_coordinates(config_path, points[0], points[1])
    print("Listo. He guardado las coordenadas en {}".format(config_path))


if __name__ == "__main__":
    main()
