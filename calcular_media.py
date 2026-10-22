
import csv

ARQUIVO_ENTRADA = "alunos_corrigidos.csv"
ARQUIVO_SAIDA = "resultado_final.csv"


def converter_nota(valor):
    """Converte notas para número; valores ausentes viram zero."""
    if valor is None:
        return 0.0

    valor = valor.strip().upper()

    if valor in ("", "FALTOU", "FALTA", "N/A", "-"):
        return 0.0

    # Aceita tanto vírgula quanto ponto decimal.
    valor = valor.replace(",", ".")

    try:
        return float(valor)
    except ValueError:
        print(f"Aviso: nota inválida '{valor}'. Considerando zero.")
        return 0.0


def calcular_media_provas(nota01, nota02):
    return (nota01 + nota02) / 2


def calcular_media_tfs(tf01, tf02):
    return (tf01 + tf02) / 2


def calcular_media_final(media_provas, media_tfs):
    return (media_provas * 7 + media_tfs * 3) / 10


def verificar_situacao(media_final):
    if media_final >= 7:
        return "APROVADO"
    return "REPROVADO"


def main():
    try:
        with open(
            ARQUIVO_ENTRADA,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=";")

            colunas = leitor.fieldnames or []
            colunas_normalizadas = {
                coluna.strip().upper(): coluna
                for coluna in colunas
            }

            obrigatorias = [
                "NOME", "RA", "NOTA01", "TF01", "NOTA02", "TF02"
            ]

            faltando = [
                coluna for coluna in obrigatorias
                if coluna not in colunas_normalizadas
            ]

            if faltando:
                print("Erro: colunas não encontradas:", faltando)
                print("Confira o cabeçalho do arquivo CSV.")
                return

            alunos = list(leitor)

    except FileNotFoundError:
        print(f"Erro: arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
        print("Coloque o CSV na mesma pasta deste programa.")
        return

    campos_saida = [
        "Nome",
        "RA",
        "Nota01",
        "TF01",
        "Nota02",
        "TF02",
        "Media_Provas",
        "Media_TFs",
        "Media_Final",
        "Situacao"
    ]

    enviados = 0
    aprovados = 0
    reprovados = 0

    with open(
        ARQUIVO_SAIDA,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo_saida:
        escritor = csv.DictWriter(
            arquivo_saida,
            fieldnames=campos_saida,
            delimiter=";"
        )
        escritor.writeheader()

        for aluno in alunos:
            dados = {
                chave.strip().upper(): valor
                for chave, valor in aluno.items()
                if chave is not None
            }

            nome = (dados.get("NOME") or "").strip()
            ra = (dados.get("RA") or "").strip()

            nota01 = converter_nota(dados.get("NOTA01"))
            tf01 = converter_nota(dados.get("TF01"))
            nota02 = converter_nota(dados.get("NOTA02"))
            tf02 = converter_nota(dados.get("TF02"))

            media_provas = calcular_media_provas(nota01, nota02)
            media_tfs = calcular_media_tfs(tf01, tf02)
            media_final = calcular_media_final(
                media_provas, media_tfs
            )

            situacao = verificar_situacao(media_final)

            if situacao == "APROVADO":
                aprovados += 1
            else:
                reprovados += 1

            escritor.writerow({
                "Nome": nome,
                "RA": ra,
                "Nota01": nota01,
                "TF01": tf01,
                "Nota02": nota02,
                "TF02": tf02,
                "Media_Provas": f"{media_provas:.2f}".replace(".", ","),
                "Media_TFs": f"{media_tfs:.2f}".replace(".", ","),
                "Media_Final": f"{media_final:.2f}".replace(".", ","),
                "Situacao": situacao
            })

            enviados += 1

            print(
                f"{nome or 'Sem nome'} | "
                f"RA: {ra or 'Sem RA'} | "
                f"Média: {media_final:.2f} | "
                f"{situacao}"
            )

    print("\n========== RESULTADO FINAL ==========")
    print(f"Total de alunos: {enviados}")
    print(f"Aprovados: {aprovados}")
    print(f"Reprovados: {reprovados}")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
