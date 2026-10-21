#!/usr/bin/env python3
"""Actualiza fronteras de series de la DGT (sin almacenar datos personales)."""
import datetime as dt
import io
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data' / 'dgt.json'
LETTERS = 'BCDFGHJKLMNPRSTVWXYZ'
HEADER = re.compile(r'[ÚU]LTIMA\s+MATR[IÍ]CULA\s+ASIGNADA\s*:\s*([BCDFGHJKLMNPRSTVWXYZ]{3})', re.I)
# Cabecera real: «Letras de la serie de la última matrícula asignada: XXX».
SERIE = re.compile(r'\b(?:LETRAS\s+DE\s+LA\s+)?SERIE\s+DE\s+LA\s+[ÚU]LTIMA\s+MATR[IÍ]CULA\s+ASIGNADA\s*:\s*([BCDFGHJKLMNPRSTVWXYZ]{3})', re.I)

def index(letters):
    n = 0
    for letter in letters:
        if letter not in LETTERS:
            return -1
        n = n * len(LETTERS) + LETTERS.index(letter)
    return n

def get_series(date, monthly=False):
    y, m = date.year, date.month
    folder = f'https://www.dgt.es/microdatos/salida/{y}/{m}/vehiculos/matriculaciones/'
    stamp = date.strftime('%Y%m' if monthly else '%Y%m%d')
    name = f'export_mensual_mat_{stamp}.zip' if monthly else f'export_mat_{stamp}.zip'
    request = urllib.request.Request(folder + name, headers={'User-Agent': 'MatriculasEspana-OpenData/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=32) as response:
            raw = response.read(45_000_000)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            txt = next((n for n in archive.namelist() if n.lower().endswith('.txt')), None)
            if not txt:
                return None
            with archive.open(txt) as stream:
                head = stream.read(4096).decode('latin-1', errors='replace').upper().replace('\ufeff', '')
        match = SERIE.search(head) or HEADER.search(head)
        return match.group(1) if match else None
    except (urllib.error.URLError, TimeoutError, zipfile.BadZipFile, OSError, ValueError) as exc:
        print(f'No disponible: {stamp}: {exc}')
        return None

def main():
    existing = json.loads(DEST.read_text('utf-8')) if DEST.exists() else {}
    history = existing.get('daily', {})
    today = dt.datetime.now(dt.timezone.utc).date()
    # Reintentamos 32 días y completamos huecos en sucesivas ejecuciones.
    new = 0
    for days in range(32, -1, -1):
        day = today - dt.timedelta(days=days)
        key = day.isoformat()
        if key in history:
            continue
        series = get_series(day)
        if series and index(series) >= 0:
            history[key] = series
            new += 1
    # Corrección de fronteras mensuales con la última cabecera diaria observada.
    month_ends = dict(existing.get('monthEnds', {}))
    for date_string, letters in sorted(history.items()):
        month = date_string[:7]
        if month > today.strftime('%Y-%m'):
            continue
        prior = month_ends.get(month)
        if prior is None or date_string > prior['date']:
            month_ends[month] = {'date': date_string, 'letters': letters, 'source': 'DGT-diario'}
    # Series mensuales cerradas: fuentes más completas cuando la DGT publica el ZIP.
    for offset in (1, 2):
        y = today.year
        m = today.month - offset
        while m <= 0:
            m += 12
            y -= 1
        key = f'{y:04d}-{m:02d}'
        if month_ends.get(key, {}).get('source') == 'DGT-mensual':
            continue
        letters = get_series(dt.date(y, m, 1), monthly=True)
        if letters:
            month_ends[key] = {'date': (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)).isoformat(), 'letters': letters, 'source': 'DGT-mensual'}
    # Nunca retroceder en serie por una publicación anómala.
    cleaned = {}
    last = -1
    for key, data in sorted(month_ends.items()):
        rank = index(data['letters'])
        if rank < last:
            print('Frontera no monótona descartada:', key)
            continue
        cleaned[key] = data
        last = rank
    payload = {'updatedAt': today.isoformat() if new or any(x.get('source')=='DGT-mensual' for x in cleaned.values()) else existing.get('updatedAt'), 'source': 'https://www.dgt.es/',
               'daily': dict(sorted(history.items())), 'monthEnds': cleaned}
    DEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Actualización completada; {new} días añadidos; {len(cleaned)} meses.')

if __name__ == '__main__':
    main()
