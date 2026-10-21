# Matrículas Españolas · GitHub Pages

Buscador de antigüedad por mes de matrícula. Mantiene el diseño original de Yeray Santos (fecha blanca, estrella dorada, antigüedad azul).

## Instalación en SaintHax/Matriculas

Conservar el logotipo `Matriculas Españolas.webp`. Subir a la rama `main` **el contenido de esta carpeta**, respetando las rutas:

- `index.html`
- `data/dgt.json`
- `scripts/update_dgt.py`
- `.github/workflows/actualizar-dgt.yml`
- `README.md`

En GitHub: Settings → Actions → General → Workflow permissions → Read and write permissions. En Actions ejecutar **Actualizar matriculas DGT → Run workflow**. Pages: Deploy from a branch → `main` → `/(root)`.

## Fiabilidad

- La DGT publica ZIP diarios con **la serie de las tres letras de la última matrícula**, no las matrículas completas de todos los vehículos. [Listado DGT](https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/matriculaciones-automoviles-diario.html).
- Las referencias de **matrícula completa** ya integradas en `index.html` (2020–agosto 2026) permiten acotar el mes con más precisión; son referencias históricas del proyecto, no certificados individuales de la DGT.
- Las referencias antiguas por serie solamente pueden ser aproximadas cerca de cambios de mes. No son certificados de matriculación.
- Para las series posteriores al último mes de matrícula completa sólo se muestra un mes si dos límites públicos permiten acotarlo. Si no hay base suficiente, aparece **Fecha no disponible**.
- Los ciclomotores admiten `C 0000 BBB` (y separadores equivalentes), pero **no** se les atribuye un mes sin tabla verificable de su serie específica. Una tabla de turismos no sirve para las matrículas C. La norma oficial está en el [BOE](https://www.boe.es/eli/es/rd/1998/12/23/2822/con/20260130).
- Los permisos provinciales se tratan por separado. La serie `TF` posee referencias aproximadas históricas; otras provincias no tienen todavía una base suficiente.

## Actualización

La automatización intenta consultar los ZIP diarios recientes, reintentar los días no publicados y usar los ZIP mensuales cuando están disponibles. No sube datos personales. El sello `Actualizado DD-MM-AAAA` refleja el último día de referencia registrado en los datos, no la fecha de ejecución del workflow. Si la DGT falla, conserva el histórico.

**Limitación esencial:** el número concreto dentro de una serie puede cambiar el mes cerca de su frontera. El sistema no puede certificar la fecha exacta de una matrícula sólo con esos ZIP. Para una fecha oficial es necesario el permiso de circulación o el informe individual de la DGT.

## Prueba

- `9099 NTF` → Octubre de 2026 (referencias de fin de septiembre NSZ y comienzos de octubre NTF).
- `C-1234-BBB` → formato de ciclomotor reconocido; fecha no disponible hasta tener fronteras específicas verificables.
- `1234 ABC` → no aceptada porque incluye vocales, ajenas a la serie moderna.


## Ciclomotores (50 cc)
- `data/ciclomotores.json`: referencias independientes para las matrículas `C-0000-BBB`.
- `scripts/update_ciclomotores.py`: intenta recuperar nuevas matrículas observadas con fecha explícita. Si no encuentra datos válidos, conserva las referencias anteriores.
- Para bloques sin límites mensuales completos se muestra intervalo de años, no una fecha inventada. En tramos acotados con menos de 30 meses, se muestra `≈` para un mes interpolado.
- Fuente de los hitos históricos: https://matriculasdelmundo.com/fechas-matriculas-motos.php ; observación reciente: https://www.seisenlinea.com/ultima-matricula/ ; inicio normativo: RD 2822/1998.
- La automatización no certifica fechas individuales ni garantiza cobertura de todos los meses.
