# Matrículas Españolas — GitHub Pages

Publica **estos archivos manteniendo las carpetas** en la rama que sirve GitHub Pages.

- `index.html` — buscador responsive; no requiere backend.
- `data/dgt.json` — últimas series públicas disponibles. La web lo consulta al abrir y cada 6 horas si permanece abierta.
- `scripts/update_dgt.py` — descarga los ZIP públicos de matriculaciones de la DGT, reconoce la cabecera de última serie y actualiza el JSON, conservando lo que ya conoce.
- `.github/workflows/actualizar-dgt.yml` — GitHub Actions, 07:17 / 13:17 / 19:17 UTC y activación manual.

## Instalación

1. Sube todo el contenido de esta carpeta a la raíz del repositorio de GitHub Pages (`main`, o la rama publicada en Pages).
2. En **Settings → Actions → General → Workflow permissions**, habilita **Read and write permissions** para permitir que la acción publique cambios, si la política del repositorio lo permite.
3. En **Actions → Actualizar matriculas DGT → Run workflow**, inicia la primera sincronización y verifica los mensajes. Los datos visibles sólo cambiarán si la DGT responde y GitHub Actions puede publicar el JSON actualizado.
4. Abre GitHub Pages y prueba `9099 NTF`, `C-0000-BRB`, `C0000BWB` y una matrícula antigua `TF 1234 AB`.

## Precisión y límites

- Los ZIP públicos de la DGT tienen **la última serie de tres letras**, no el número completo ni la matrícula del vehículo para cada registro. Por eso la actualización automática produce **estimaciones por mes**; no una fecha exacta garantizada.
- Se conserva la tabla detallada preexistente de matrículas completas (2020–agosto de 2026) sin sustituirla por una estimación menos fina.
- Para ciclomotores se reconocen matrículas `C 0000 BBB` y se muestran referencias históricas amplias; no se inventa una fecha exacta para series nuevas. El formato `C-0000-XX` se admite como entrada parcial, pero **no es una matrícula nacional actual completa**: faltaría una tercera letra.
- Otros provinciales antiguos se reconocen, pero sólo TF cuenta con tabla histórica en esta entrega. No hay consultas de propietarios ni acceso a datos personales.
- La DGT puede cambiar disponibilidad, formato o URL; si falla una descarga, se conserva el JSON publicado previamente.
- Las entradas iniciales del JSON de octubre 2026 son referencias públicas contrastadas a 19/10/2026, **no se han descargado en esta sesión directamente desde los ZIP de la DGT**. Se irán sustituyendo por registros de descarga según haya datos disponibles.

Fuentes: https://www.dgt.es/menusecundario/dgt-en-cifras/ y https://www.boe.es/eli/es/rd/1998/12/23/2822/con/

## Respaldo integrado

El HTML incorpora dos referencias de serie (septiembre y octubre de 2026) para que una caída
de `data/dgt.json` no deje sin respuesta a series como NTF. El mes mostrado es orientativo,
NO la fecha individual certificada de matriculación. Las series futuras requieren nuevos
datos publicados por la DGT.

Nota: GitHub Actions actualiza el repositorio, pero GitHub Pages debe estar configurado
para publicar desde la rama/carpeta que contiene también `data/dgt.json`.
