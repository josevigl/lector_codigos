import argparse
import logging
import signal
import threading

import yaml

from core.pipeline import DetectorPipeline


def load_config(path):
    with open(path, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    if not isinstance(config, dict):
        raise ValueError("El archivo de configuración debe contener un mapa YAML.")
    return config


def main():
    parser = argparse.ArgumentParser(
        description="Detecta un código en una región de pantalla"
    )
    parser.add_argument("--config", default="config.yaml", help="Archivo de configuración")
    args = parser.parse_args()

    config = load_config(args.config)
    logging.basicConfig(
        level=getattr(logging, str(config.get("logging", {}).get("level", "INFO")).upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    stop_event = threading.Event()
    signal.signal(signal.SIGINT, lambda _signum, _frame: stop_event.set())
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, lambda _signum, _frame: stop_event.set())

    DetectorPipeline(config).run(stop_event)


if __name__ == "__main__":
    main()
