#!/usr/bin/env python3
"""Actualiza series de matrículas ordinarias desde cabeceras diarias públicas de DGT.
No contiene matrículas individuales ni atribuye fechas exactas a vehículos.
"""
import datetime as dt
import io
import json
from pathlib import Path
import re
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data' / 'dgt.json'
LETTERS = 'BCDFGHJKLMNPRSTVWXYZ'
PATTERN = re.compile(r'(?:letras\s+de\s+la\s+)?serie\s+de\s+la\s+[úu]ltima\s+matr[ií]cula\s+asignada\s*:\s*([a-z]{3})', re.I)
ALT_PATTERN = re.compile(r'[úu]ltima\s+matr[ií]cula\s+asignada\s*:\s*([a-z]{3})', re.I)


def rank(value):
    if not isinstance(value, str) or len(value) != 3 or any(x not in LETTERS for x in value):
        return -1
    n = 0
    for letter in value:
        n = n * len(LETTERS) + LETTERS.index(letter)
    return n


def parse_header(data):
    # La cabecera es texto; los registros de abajo son de ancho fijo (NO CSV).
    line = data.decode('latin-1', errors='replace').replace('\ufeff', '').splitlines()[0] if data else ''
    line = ' '.join(line.split())
    match = PATTERN.search(line) or ALT_PATTERN.search(line)
    value = match.group(1).upper() if match else None
    return value if rank(value) >= 0 else None


def get_series(day, monthly=False):
    stamp = day.strftime('%Y%m' if monthly else '%Y%m%d')
    name = f'export_mensual_mat_{stamp}.zip' if monthly else f'export_mat_{stamp}.zip'
    url = f'https://www.dgt.es/microdatos/salida/{day.year}/{day.month}/vehiculos/matriculaciones/{name}'
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; MatriculasOpenData/2.0)'})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = response.read(45_000_001)
        if len(payload) > 45_000_000:
            raise ValueError('ZIP supera límite de seguridad')
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            entries = [e for e in archive.infolist() if e.filename.lower().endswith('.txt') and not e.is_dir()]
            for entry in entries:
                with archive.open(entry) as stream:
                    series = parse_header(stream.read(2048))
                    if series:
                        return series
        print(f'Sin cabecera de serie reconocible: {stamp}')
    except (urllib.error.URLError, TimeoutError, zipfile.BadZipFile, OSError, ValueError, EOFError) as exc:
        print(f'No disponible {stamp}: {exc}')
    return None


def main():
    data = json.loads(DEST.read_text(encoding='utf-8')) if DEST.exists() else {}
    history = {k:v for k,v in data.get('daily', {}).items() if rank(v)>=0 and re.fullmatch(r'\d{4}-\d{2}-\d{2}', k)}
    monthly = dict(data.get('monthEnds', {}))
    today = dt.datetime.now(dt.timezone.utc).date()
    successes = 0
    # 45 días: cubre retrasos, fines de semana y cambio de mes.
    for delta in range(45, -1, -1):
        day = today - dt.timedelta(days=delta)
        key = day.isoformat()
        if key in history:
            continue
        value = get_series(day)
        if value:
            history[key] = value
            successes += 1
    for offset in (1, 2):
        year, month = today.year, today.month - offset
        while month <= 0:
            year -= 1
            month += 12
        key = f'{year:04d}-{month:02d}'
        if monthly.get(key, {}).get('source') == 'DGT-mensual':
            continue
        value = get_series(dt.date(year, month, 1), monthly=True)
        if value:
            dates = [k for k in history if k.startswith(key)]
            # Este valor es sólo el límite de serie, NO la matrícula completa.
            monthly[key] = {'date': max(dates) if dates else key+'-01', 'letters': value, 'source': 'DGT-mensual'}
            successes += 1
    # Deriva las referencias mensuales del último DÍA REAL disponible, sin
    # etiquetar como fin de mes un mes que aún está en curso.
    for key, letters in sorted(history.items()):
        ym = key[:7]
        existing = monthly.get(ym)
        if existing and existing.get('source') == 'DGT-mensual':
            continue
        if not existing or key > existing.get('date', ''):
            monthly[ym] = {'date':key, 'letters':letters, 'source':'DGT-diario'}
    # No actualizamos el sello con la fecha actual si no entraron datos públicos.
    date_candidates = [k for k in history if re.fullmatch(r'\d{4}-\d{2}-\d{2}',k)]
    updated_at = max(date_candidates) if date_candidates else data.get('updatedAt')
    cleaned = {k:v for k,v in sorted(monthly.items()) if isinstance(v,dict) and rank(v.get('letters')) >= 0}
    output = {'updatedAt':updated_at, 'source':'https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/matriculaciones-automoviles-diario.html',
              'daily':dict(sorted(history.items())), 'monthEnds':cleaned}
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Días nuevos: {successes}; referencias diarias: {len(history)}; último dato: {updated_at or "ninguno"}')


if __name__ == '__main__':
    main()
