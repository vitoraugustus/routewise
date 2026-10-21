import unicodedata

linhas = [
    {"nome": "INTER-2 (HORÁRIO) - 022", "paradas": ["Terminal Cabral", "Estação Tubo Agrárias", "Estação Tubo Praça das Nações", "Estação Tubo Colégio Militar", "Terminal Capão da Imbuia"], "minutos": 36, "tarifa": 6.00},
    {"nome": "INTER-2 (ANTI-HORÁRIO) - 023", "paradas": ["Terminal Capão da Imbuia", "Av. Victor Ferreira do Amaral", "Rua dos Funcionários", "Rua Luciano Cardinale", "Terminal Cabral"], "minutos": 43, "tarifa": 6.00}
]

def normalizar(texto):
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")

def buscar_rotas(origem, destino, prioridade):
    origem = normalizar(origem)
    destino = normalizar(destino)
    opcoes = []
    for linha in linhas:
        p = [normalizar(parada) for parada in linha["paradas"]]
        if origem in p and destino in p and p.index(origem) < p.index(destino):
            opcoes.append(linha)

    chave = "tarifa" if prioridade == "custo" else "minutos"
    return sorted(opcoes, key=lambda linha: linha[chave])
