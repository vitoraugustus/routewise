import json
import re
import unicodedata
from pathlib import Path

ARQUIVO = Path(__file__).parent / "linhas.json"


def carregar_linhas(caminho=ARQUIVO):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def limpar_parada(texto):
    """Extrai apenas a rua e número, removendo bairro e vírgulas."""
    padrao = r"^(.*?\b\d+(?:-\d+)?)"
    match = re.match(padrao, texto.strip())

    if match:
        resultado = match.group(1)
        return resultado.replace(",", "").strip()

    return texto.strip().replace(",", "")


def normalizar(texto):
    texto_limpo = limpar_parada(texto)
    
    texto_nfd = unicodedata.normalize("NFD", texto_limpo.lower())
    texto_final = "".join(c for c in texto_nfd if unicodedata.category(c) != "Mn")

    texto_final = re.sub(r"^(r\.|rua|av\.|avenida|praça|praca)\s+", "", texto_final)

    substituicoes = {
        r"\bmaier\b": "mayer",
        r"\bpadre\b": "pe",
    }

    for original, substituto in substituicoes.items():
        texto_final = re.sub(original, substituto, texto_final)

    return texto_final.strip()


def buscar_rotas(linhas, origem, destino, prioridade):
    origem_norm = normalizar(origem)
    destino_norm = normalizar(destino)
    opcoes = []

    for linha in linhas:
        p = [normalizar(parada) for parada in linha["paradas"]]

        tempos_validos = [
            sum(linha["tempos"][i:j])
            for i, nome_i in enumerate(p) if origem_norm in nome_i
            for j, nome_j in enumerate(p) if destino_norm in nome_j and i < j
        ]

        if tempos_validos:
            opcao = dict(linha)
            opcao["tempo"] = min(tempos_validos)
            opcoes.append(opcao)

    chave = "tarifa" if prioridade == "custo" else "tempo"
    return sorted(opcoes, key=lambda l: l.get(chave, l["tempo"]))