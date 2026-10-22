
import csv
import random
import re
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ARQUIVO_ENTRADA = PASTA / "alunos.csv"
ARQUIVO_SAIDA = PASTA / "alunos_corrigidos.csv"

random.seed(42)

COLUNAS = ["Nome", "RA", "Nota01", "TF01", "Nota02", "TF02"]


def limpar_nome(valor):
    return re.sub(r"\s+", " ", str(valor or "")).strip().title()


def limpar_ra(valor, usados):
    ra = re.sub(r"\D", "", re.sub(r"(?i)^RA", "", str(valor or "").strip()))

    if not ra or ra in usados:
        while True:
            ra = str(random.randint(100101, 999999))
            if ra not in usados:
                break

    usados.add(ra)
    return ra


def converter_nota(valor):
    valor = str(valor or "").strip().upper()

    if valor in ("", "FALTOU", "FALTA", "N/A", "NA", "-", "NONE", "NAN"):
        return round(random.uniform(0, 10), 1)

    try:
        nota = float(valor.replace(",", "."))
    except ValueError:
        return round(random.uniform(0, 10), 1)

    return round(max(0, min(10, nota)), 1)


def main():
    print("Pasta do programa:", PASTA)
    print("Procurando arquivo:", ARQUIVO_ENTRADA)

    if not ARQUIVO_ENTRADA.is_file():
        print("ERRO: alunos.csv não foi encontrado.")
        return

    with open(ARQUIVO_ENTRADA, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        if not leitor.fieldnames:
            print("ERRO: CSV sem cabeçalho.")
            return

        leitor.fieldnames = [c.strip() for c in leitor.fieldnames]

        faltantes = set(COLUNAS) - set(leitor.fieldnames)
        if faltantes:
            print("ERRO: colunas ausentes:", sorted(faltantes))
            print("Cabeçalho encontrado:", leitor.fieldnames)
            return

        alunos = [
            linha for linha in leitor
            if any(str(v or "").strip() for v in linha.values())
        ]

    usados = set()
    corrigidos = []

    for i, aluno in enumerate(alunos, start=1):
        nome = limpar_nome(aluno.get("Nome"))
        if not nome or nome.lower() == "nome":
            nome = f"Aluno Teste {i:03d}"

        ra = limpar_ra(aluno.get("RA"), usados)

        corrigidos.append({
            "Nome": nome,
            "RA": ra,
            "Nota01": f"{converter_nota(aluno.get('Nota01')):.1f}",
            "TF01": f"{converter_nota(aluno.get('TF01')):.1f}",
            "Nota02": f"{converter_nota(aluno.get('Nota02')):.1f}",
            "TF02": f"{converter_nota(aluno.get('TF02')):.1f}",
        })

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS, delimiter=";")
        escritor.writeheader()
        escritor.writerows(corrigidos)

    print("\nCORREÇÃO CONCLUÍDA!")
    print("Alunos processados:", len(corrigidos))
    print("Arquivo criado:", ARQUIVO_SAIDA)
    print("Arquivo existe?", ARQUIVO_SAIDA.exists())


if __name__ == "__main__":
    main()
