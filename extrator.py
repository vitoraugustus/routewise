import csv
import json
import math
import re
from pathlib import Path

PASTA = Path(__file__).parent / "gtfs"      
SAIDA = Path(__file__).parent / "linhas.json"

TARIFA = 6.00

# Lines to extract. route_id: total trip time in minutes
LINHAS_DESEJADAS = {
    "010": 45,
    "011": 70,
    "020": 120,
    "021": 120,
    "022": 36,
    "023": 43,
    "030": 98,
    "040": 100,
    "050": 55,
    "216": 41,
    "250": 55,
    "303": 57,
    "350": 34
    
}


def ler_rotas():
    with open(PASTA / "routes.txt", encoding="utf-8-sig", newline="") as f:
        return {r["route_id"]: r["route_long_name"] for r in csv.DictReader(f)}


def limpar_nome(nome):
    """'Terminal Cabral - 022 - Inter 2 (Horario)' -> 'Terminal Cabral'."""
    nome = re.split(r"\s+-\s*(?:\d|Inter)", nome)[0]
    return " ".join(nome.split())


def ler_paradas():
    with open(PASTA / "stops.txt", encoding="utf-8-sig", newline="") as f:
        return {
            r["stop_id"]: {
                "nome": limpar_nome(r["stop_name"]),
                "lat": float(r["stop_lat"]),
                "lon": float(r["stop_lon"]),
            }
            for r in csv.DictReader(f)
        }


def ler_viagens_modelo():
    """For each (route, direction), keeps the stop sequence of the first trip found."""
    viagens = {}
    with open(PASTA / "stop_times.txt", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            route_id = r["trip_id"].split("_")[0]
            if route_id not in LINHAS_DESEJADAS:
                continue
            viagens.setdefault(r["trip_id"], []).append((int(r["stop_sequence"]), r["stop_id"]))

    modelos = {}
    for trip_id, paradas in viagens.items():
        seq = tuple(stop_id for _, stop_id in sorted(paradas))
        modelos.setdefault((trip_id.split("_")[0], seq), seq)
    return modelos


def distancia_km(a, b):
    """Haversine distance between two points (lat/lon in degrees)."""
    r = 6371.0
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp = p2 - p1
    dl = math.radians(b["lon"] - a["lon"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def dividir_tempo(paradas, total_min):
    """Splits total_min across the segments in proportion to their distance
    (largest-remainder rounding, so the sum is exact and no segment goes negative)."""
    dists = [distancia_km(a, b) for a, b in zip(paradas, paradas[1:])]
    soma = sum(dists) or 1
    exatos = [total_min * d / soma for d in dists]
    tempos = [int(x) for x in exatos]
    faltam = total_min - sum(tempos)
    por_resto = sorted(range(len(exatos)), key=lambda i: exatos[i] - tempos[i], reverse=True)
    for i in por_resto[:faltam]:
        tempos[i] += 1
    return tempos


def main():
    rotas = ler_rotas()
    paradas = ler_paradas()
    modelos = ler_viagens_modelo()

    linhas = []
    for (route_id, seq), _ in sorted(modelos.items()):
        pontos = [paradas[s] for s in seq]
        linhas.append({
            "nome": f"{rotas[route_id]} - {route_id}",
            "paradas": [p["nome"] for p in pontos],
            "tempos": dividir_tempo(pontos, LINHAS_DESEJADAS[route_id]),
            "tarifa": TARIFA,
        })

    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(linhas, f, ensure_ascii=False, indent=2)
    print(f"{len(linhas)} linha(s) salva(s) em {SAIDA}")


if __name__ == "__main__":
    main()