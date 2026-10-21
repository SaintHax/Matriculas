#!/usr/bin/env python3
"""Añade únicamente hitos de ciclomotores verificables en fuente pública.
Si la página cambia o no se reconoce la matrícula, conserva lo anterior.
"""
import datetime as dt
import json
from pathlib import Path
import re
import urllib.request
from html import unescape

OUT = Path(__file__).resolve().parents[1] / "data" / "ciclomotores.json"
URL = "https://www.seisenlinea.com/ultima-matricula/"
PAT = re.compile(r"C\s*([0-9])\s*([0-9]{3})\s*([BCDFGHJKLMNPRSTVWXYZ]{3})", re.I)

def main():
    data=json.loads(OUT.read_text(encoding="utf8"))
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; OpenDataMatriculas/1.0)"})
    try:
        with urllib.request.urlopen(req,timeout=20) as resp:
            html=resp.read(500000).decode("utf-8","replace")
        text=unescape(re.sub(r"<[^>]*>"," ",html))
        text=re.sub(r"\s+"," ",text)
        marker=text.lower().find("última matrícula de ciclomotor")
        segment=text[marker:marker+360] if marker>=0 else ""
        match=PAT.search(segment)
        today=dt.datetime.now(dt.timezone.utc).date()
        # Se exige una fecha publicada inequívoca (no se utiliza automáticamente hoy).
        d=re.search(r"(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)?\s*\(?([0-3]?\d)/([01]?\d)/(20\d{2})\)?",segment,re.I)
        if not match or not d:
            print("Sin referencia de matrícula y fecha emparejadas; no se modifica el histórico")
            return
        day=dt.date(int(d.group(3)),int(d.group(2)),int(d.group(1)))
        if day>today or (today-day).days>45:
            print("Fecha fuera de ventana; se conserva el histórico")
            return
        plate=f"C{match.group(1)}{match.group(2)}{match.group(3).upper()}"
        refs=data['references']
        if not any(r['plate']==plate and r['date']==day.isoformat() for r in refs):
            refs.append({'plate':plate,'date':day.isoformat(),'precision':'observed','source':URL})
            data['updatedAt']=day.isoformat()
            OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
            print("Guardada referencia:",plate,day)
        else: print("Referencia ya existente")
    except Exception as exc:
        print("Fuente no disponible, se conserva el archivo:",exc)

if __name__=='__main__': main()
