# Desbloqueo RTX 3090 en Windows: dónde estamos

Nota para retomar en una sesión nueva. Actualizada: 2026-11-03, 01:28.

## Pendiente, en este orden

**Conclusión de Iosu (2026-11-03):** para entrenar puede merecer la pena; para su uso normal (PDFs y chat en LM Studio),
no mucho. Windows sigue arrancando primero, sin desbloqueo.

Nada obligatorio pendiente. Solo si un día quiere entrenar con el desbloqueo:

1. Comprobar la `db` (como administrador) y, si falta el certificado, repetir el Append (ver "Estado").
2. Probar el arranque sin `U` por F8, y hacer varios ciclos de apagar y encender antes de usar `C:\start-unlock.ps1`.
3. Medir un trabajo real de Virtus Create: las cifras de abajo son con ejemplos de prueba.

## Resultados: entrenamiento

Qwen3.8-27B en 4 bits, LoRA, 30 pasos, tope de VRAM de 21 GB. Con ejemplos de prueba, no preguntas reales.

| Límite | Estado | Tiempo por paso | 1 500 pasos | BF16 | FP16 | FP32 |
|---|---|---|---|---:|---:|---:|
| 219 W | Bloqueada | 13,04 s | 326 min | 52,0 | 49,2 | 16,1 |
| 219 W | Desbloqueada | 13,01 s | 325 min | 65,9 | 61,1 | 16,1 |
| 254 W | Desbloqueada | 10,09 s | 252 min | 83,5 | 78,2 | 20,5 |
| 299 W | Desbloqueada (1.ª) | 9,28 s | 232 min | 105,3 | 98,9 | 23,1 |
| 299 W | Desbloqueada (2.ª) | 9,25 s | 231 min | 108,7 | 100,1 | 23,3 |
| 299 W | **Bloqueada** | **10,69 s** | **267 min** | 67,5 | 65,6 | 23,3 |

- **A 299 W, el desbloqueo acelera el entrenamiento un 15 %** (de 10,69 a 9,27 s por paso): unos 35 min menos en 1 500
  pasos, con el mismo consumo y temperatura (unos 297 W, 75 °C). Bloqueada solo hay una medición; desbloqueada, dos.
- A 219 W el desbloqueo no aportó nada al entrenar: +0,2 %.
- Falta el dato bloqueado a 254 W, así que el +29 % de 219 a 254 W no se puede atribuir al desbloqueo.
- Cálculo puro a 329 W: BF16 de 71,1 a 112,3 TFLOPS (+58 %), FP16 de 68,8 a 108,8, FP32 sin cambios. Es una medición
  breve de 10 muestras después del desbloqueo, frente a 30 antes.
- Gemma E4B bloqueada a 329 W: 3,89 s por paso. Iosu no lo va a usar.

## Resultados: PDFs en LM Studio

Qwen3.8-27B a 299 W, 2026-11-03, los mismos tokens en ambos casos. Detalle en `lmstudio\`.

| Documento | Desbloqueada: lectura + escritura | Bloqueada: lectura + escritura | Total desbl. | Total bloq. |
|---|---:|---:|---:|---:|
| `6pag-todobien01000909_20250509_115803_-_copy.pdf` | 93,2 + 129,2 s | 94,6 + 123,0 s | 222,4 s | 217,6 s |
| `1-Eusk-c25-16499-r.pdf` | 29,1 + 13,4 s | 29,8 + 13,1 s | 42,5 s | 42,9 s |
| `2_PRECIBALL_Invoice_125020064.pdf` | 29,9 + 33,9 s | 30,1 + 33,0 s | 63,8 s | 63,1 s |
| **Total** | 152,2 + 176,5 s | 154,5 + 169,1 s | **328,7 s** | **323,6 s** |

- **En LM Studio, el desbloqueo no acelera estos PDF:** lectura 1,5 % mejor, escritura 4 % peor. Una tanda de cada, dentro
  de lo que puede variar una ejecución. En la bloqueada no se confirmó que el modelo se recargara antes del 6 páginas; el
  log muestra lectura completa en todas las peticiones, así que no hubo reutilización.
- `12_80164940_v.pdf` falló en la aplicación con "No structured data", y la causa no se ha mirado. Queda fuera.
- Referencia con otra potencia: el 24-10, bloqueada a 329 W, un PDF con esos mismos tokens leía a 564 t/s. No sirve como
  comparación. Es posible que fuera el de Preciball, sin confirmar.

## Estado del PC

- **ASUS ProArt Z890-CREATOR WIFI, BIOS 3305**, Core Ultra 7 265, RTX 3090 Dell OEM (`10de:2204`, `1028:3880`). Pantalla:
  gafas XREAL por USB-C, desde la iGPU Intel.
- **Generador:** oscila a 314 W y aguanta estable a 299 W en pruebas cortas. No se completaron los 10 minutos ni a 294 ni
  a 299 W. Iosu prefiere no forzarlo. El límite se pierde al reiniciar.
- **Secure Boot:** en Standard desde 2026-11-03. Probablemente se perdió el certificado de la `db`, sin confirmar porque
  leerla pide administrador. Si es así, la entrada F8 dará error de certificado: repetir **Append** con
  `E:\SBKEY\GPUDB.CER` y **no** usar `C:\start-unlock.ps1` antes.
- **Pantalla parada en el logo de ASUS:** ocurrió una vez, el primer encendido normal tras una sesión desbloqueada, con
  Secure Boot en Custom. Arrancó al pasar a Standard. La causa no está demostrada: antes hubo arranques en Custom. Vigilar.
- **Recuperación:** F8 > Windows Boot Manager. Nunca restaurar claves de fábrica a la ligera.

## Dónde está todo

| Qué | Dónde |
|---|---|
| Código del desbloqueo | `C:\IA\Windows-GPU-UNLOCK`, rama `z890-intel-display`, en https://github.com/iosub/Windows-GPU-UNLOCK (commit `66afabd`) |
| EFI firmados y firmware | `E:\EFI\WindowsGPUUnlock\`, `E:\RTX3090-UNLOCK\ASSETS\` (versión manual con `U` en `MANUAL\`, sin `U` sin probar) |
| Copia de E: | `C:\IA\firmware-unlock\E-backup` |
| Clave de firma | Certificados de usuario de Windows, huella `7A742B4CC542FFAE88EB49391A772A9D7E511589`, no exportable |
| Scripts de arranque | `C:\start-unlock.ps1`, `C:\start-lock.ps1` (nombres de Iosu), `research\z890\register-unlock.ps1` |
| GPU Power, Virtus Create | `C:\IA\Berpiztu\llm-create` (`gpu-power\`, `virtus\`), en GitHub, commit `3150e1e` |
| Prueba de medición | `scripts\bench_virtus.py`; se lanza con el `.venv` de `llm-create`, modelo en `models\Qwen3.8-27B-UD-Q4_K_M-unpacked`, `--four-bits --max-vram-gb 21` |
| Estos resultados | `C:\IA\gpu-unlock\Results`, rama `z890-results`, en https://github.com/iosub/gpu-unlock |

## Lo que ya se decidió o aprendió

- `learn.py` mantiene en 16 bits lo no comprimido: la conversión a 32 bits llenaba la VRAM y hacía los pasos muy lentos.
  Falta comprobar con un trabajo real que el modelo aprende igual de bien.
- Por encima de 21 GB de VRAM, Windows desborda a la RAM y todo va muchísimo más lento.
- Posible mejora de los PDFs sin desbloqueo: las dos peticiones de cada documento vuelven a leer casi lo mismo. Aprovechar
  lo ya leído ahorraría unos 45 s en el de 6 páginas. Sin comprobar en el código.
- Commits sin atribuciones. En `llm-create`, las reglas de `rules.md` son obligatorias: las pruebas las hace Iosu.
