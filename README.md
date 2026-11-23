# Detector de códigos para un directo

Este proyecto empezó con una idea bastante concreta: mientras veía un directo de GTA VI
de elRubius, quería probar si podía reconocer un código que aparecía unos
segundos sobre el vídeo y copiarlo antes de escribirlo a mano.

Al final, elRubius comentó que repartiría los códigos por mensaje privado para
evitar scripts. Eso dejó de lado el caso original, pero el prototipo me sirvió
para experimentar con captura de pantalla, OCR local y automatización en
Windows. El programa solo analiza una región visible de la pantalla; no lee el
chat ni los mensajes privados.

## Qué hace

- Captura una región de pantalla con DXcam (Desktop Duplication de Windows).
- Compara frames para no ejecutar OCR si la región no ha cambiado.
- Mejora el contraste y reconoce texto localmente con RapidOCR.
- Acepta códigos de 12 caracteres, con o sin el formato visual
  `XXXX-XXXX-XXXX`; al portapapeles copia los 12 caracteres sin guiones.
- Evita volver a procesar un código durante el tiempo configurado y registra
  tiempos de captura, OCR y copia sin escribir el código en los logs.
- Opcionalmente, pega el código en un campo y pulsa **Continuar**. Esa acción
  está desactivada por defecto; no automatiza los pasos posteriores del canje.

El OCR mide alrededor de 21 ms de mediana en una prueba local con una imagen de
ejemplo. Es una medición pequeña, no una garantía de latencia en directo: el
resultado cambia según el equipo, el tamaño de la región y la calidad del vídeo.

## Prepararlo en Windows

El proyecto usa Python 3.10 porque es la versión declarada compatible por
RapidOCR 1.2.3.

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item config.example.yaml config.yaml
```

La primera inicialización de RapidOCR puede descargar los modelos. Después,
el reconocimiento se ejecuta localmente.

## Probarlo

1. Ejecuta `python select_roi.py`, selecciona el código completo con algo de
   margen y pulsa `Enter`. Copia la ROI impresa en `capture.roi` de
   `config.yaml`. El formato es `[izquierda, arriba, derecha, abajo]`, no
   `[x, y, ancho, alto]`.
2. Ejecuta `python main.py`. Cuando encuentre un código válido, lo copia al
   portapapeles y emite un sonido. Para detenerlo, pulsa `Ctrl+C`.

Si quieres probar el pegado y el botón **Continuar**, coloca las ventanas como
piensas usarlas y ejecuta `python select_actions.py`. En la captura mostrada,
haz clic primero en el centro del campo y luego en el botón. El selector guarda
las coordenadas en `config.yaml` y activa la automatización. Mantén las ventanas
en la misma posición y tamaño mientras el detector esté funcionando. Para
volver al modo de solo copia, cambia `automation.enabled` a `false`.

## Decisiones y límites

- El reconocimiento está ajustado a una sola línea horizontal dentro de una
  región fija. Si la ROI contiene varias líneas o texto inclinado, puedes
  activar `use_text_detection` o `use_angle_classifier` en la configuración.
- No se corrigen automáticamente confusiones como `O/0` o `I/1`: una
  sustitución podría convertir un error de OCR en otro código.
- La automatización de pantalla depende de que las ventanas no se muevan y de
  que las coordenadas sigan apuntando al campo y al botón correctos.
- No se ha medido el tiempo desde que un código aparece en el stream. Los
  percentiles que muestra el programa cubren etapas internas, no la latencia
  completa de Twitch.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```
