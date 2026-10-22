
import csv
import re
import time
from pathlib import Path

import requests

PASTA = Path(__file__).resolve().parent

ARQUIVO_CSV = PASTA / "alunos_corrigidos.csv"
ARQUIVO_RELATORIO = PASTA / "resultado_envios.csv"

URL_FORM = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSf8TNT9H-vrVK9N0GS5aAoo1KP6hkZk-FlqD0YhoWI0Foztmw/"
    "formResponse"
)

CAMPOS = {
    "RA": "entry.1589499249",
    "Nome": "entry.1952665221",
    "Nota01": "entry.1175366815",
    "Nota02": "entry.1832190031",
    "TF01": "entry.118364229",
    "TF02": "entry.2009296790",
}

COLUNAS_RELATORIO = [
    "Nome", "RA", "HTTP", "Status", "URL_final"
]


def limpar_texto(valor):
    return str(valor or "").strip()


def limpar_ra(valor):
    valor = re.sub(r"(?i)^RA", "", limpar_texto(valor))
    return re.sub(r"\D", "", valor)


def limpar_nota(valor):
    valor = limpar_texto(valor).upper()

    if valor in ("", "FALTOU", "FALTA", "N/A", "-"):
        return "0"

    try:
        nota = float(valor.replace(",", "."))
    except ValueError:
        raise ValueError(f"Nota inválida: {valor!r}")

    if not 0 <= nota <= 10:
        raise ValueError(f"Nota fora do intervalo de 0 a 10: {valor}")

    return f"{nota:g}"


def carregar_alunos():
    if not ARQUIVO_CSV.is_file():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO_CSV}"
        )

    with open(
        ARQUIVO_CSV,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        if not leitor.fieldnames:
            raise ValueError("O CSV não possui cabeçalho.")

        leitor.fieldnames = [
            campo.strip() for campo in leitor.fieldnames
        ]

        faltantes = set(CAMPOS) - set(leitor.fieldnames)

        if faltantes:
            raise ValueError(
                f"Colunas ausentes: {sorted(faltantes)}. "
                f"Cabeçalho encontrado: {leitor.fieldnames}"
            )

        return list(leitor)


def preparar_dados(aluno):
    dados = {
        "RA": limpar_ra(aluno.get("RA")),
        "Nome": limpar_texto(aluno.get("Nome")),
        "Nota01": limpar_nota(aluno.get("Nota01")),
        "Nota02": limpar_nota(aluno.get("Nota02")),
        "TF01": limpar_nota(aluno.get("TF01")),
        "TF02": limpar_nota(aluno.get("TF02")),
    }

    if not dados["Nome"] or not dados["RA"]:
        raise ValueError("Nome ou RA vazio.")

    return {
        codigo: dados[campo]
        for campo, codigo in CAMPOS.items()
    }


def enviar_aluno(sessao, aluno):
    dados = preparar_dados(aluno)

    resposta = sessao.post(
        URL_FORM,
        data=dados,
        timeout=30,
        allow_redirects=True,
        headers={
            "Referer": URL_FORM.replace(
                "formResponse", "viewform"
            ),
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
            ),
        },
    )

    texto = resposta.text.lower()

    frases_confirmacao = (
        "sua resposta foi registrada",
        "your response has been recorded",
        "response has been recorded",
        "resposta foi registrada",
    )

    if resposta.status_code != 200:
        status = "ERRO_HTTP"
    elif any(frase in texto for frase in frases_confirmacao):
        status = "CONFIRMACAO_ENCONTRADA"
    else:
        status = "NAO_CONFIRMADO"

    return {
        "Nome": limpar_texto(aluno.get("Nome")),
        "RA": limpar_ra(aluno.get("RA")),
        "HTTP": resposta.status_code,
        "Status": status,
        "URL_final": resposta.url,
    }


def salvar_relatorio(resultados):
    with open(
        ARQUIVO_RELATORIO,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=COLUNAS_RELATORIO,
            delimiter=";"
        )
        escritor.writeheader()
        escritor.writerows(resultados)


def main():
    try:
        alunos = carregar_alunos()
    except (OSError, ValueError) as erro:
        print("ERRO:", erro)
        return

    if not alunos:
        print("O CSV não possui alunos.")
        return

    # Inclui todos os alunos, inclusive Lucas Rodrigues.
    resultados = []

    print("Alunos encontrados:", len(alunos))
    print("Envios programados:", len(alunos))
    print("Iniciando envio...\n")

    with requests.Session() as sessao:
        for indice, aluno in enumerate(alunos, start=1):
            nome = limpar_texto(aluno.get("Nome"))

            try:
                resultado = enviar_aluno(sessao, aluno)
            except (requests.RequestException, ValueError) as erro:
                resultado = {
                    "Nome": nome,
                    "RA": limpar_ra(aluno.get("RA")),
                    "HTTP": "",
                    "Status": "ERRO",
                    "URL_final": str(erro),
                }

            resultados.append(resultado)

            # Salva o progresso após cada aluno.
            salvar_relatorio(resultados)

            print(
                f"[{indice}/{len(alunos)}] "
                f"{resultado['Nome']} | "
                f"RA: {resultado['RA']} | "
                f"HTTP: {resultado['HTTP']} | "
                f"{resultado['Status']}"
            )

            if indice < len(alunos):
                time.sleep(2)

    confirmados = sum(
        r["Status"] == "CONFIRMACAO_ENCONTRADA"
        for r in resultados
    )

    nao_confirmados = sum(
        r["Status"] == "NAO_CONFIRMADO"
        for r in resultados
    )

    erros = sum(
        r["Status"] in ("ERRO", "ERRO_HTTP")
        for r in resultados
    )

    print("\nPROCESSO FINALIZADO")
    print("Total processado:", len(resultados))
    print("Confirmações encontradas:", confirmados)
    print("Não confirmados:", nao_confirmados)
    print("Erros:", erros)
    print("Relatório salvo em:", ARQUIVO_RELATORIO.name)
    print("\nConfira a aba Respostas do Google Forms.")


if __name__ == "__main__":
    main()
