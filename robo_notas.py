
import csv
import unicodedata
from pathlib import Path

# Arquivos possíveis, em ordem de prioridade
ARQUIVOS = [
    "alunos_atualizados.csv",
    "alunos_corrigidos.csv",
    "alunos.csv",
]

COLUNAS_NOTAS = ["Nota01", "TF01", "Nota02", "TF02"]
MEDIA_MINIMA = 6.0


def normalizar(texto):
    """Ignora acentos, espaços extras e diferenças entre maiúsculas/minúsculas."""
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )


def localizar_arquivo():
    """Encontra o primeiro arquivo CSV disponível."""
    for nome_arquivo in ARQUIVOS:
        caminho = Path(nome_arquivo)
        if caminho.exists():
            return caminho

    raise FileNotFoundError(
        "Nenhum arquivo CSV foi encontrado. "
        "Verifique se alunos.csv ou alunos_corrigidos.csv existe."
    )


def carregar_alunos():
    """Carrega os alunos do arquivo CSV."""
    caminho = localizar_arquivo()

    with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
        amostra = arquivo.read(4096)
        arquivo.seek(0)

        try:
            delimitador = csv.Sniffer().sniff(
                amostra, delimiters=";,"
            ).delimiter
        except csv.Error:
            delimitador = ";"

        leitor = csv.DictReader(arquivo, delimiter=delimitador)

        if not leitor.fieldnames:
            raise ValueError("O arquivo CSV está vazio ou sem cabeçalho.")

        # Remove espaços dos nomes das colunas
        leitor.fieldnames = [
            coluna.strip() for coluna in leitor.fieldnames
        ]

        colunas_obrigatorias = ["Nome", "RA"] + COLUNAS_NOTAS
        faltantes = [
            coluna
            for coluna in colunas_obrigatorias
            if coluna not in leitor.fieldnames
        ]

        if faltantes:
            raise ValueError(
                "Faltam estas colunas no CSV: " + ", ".join(faltantes)
            )

        alunos = []
        for linha in leitor:
            # Ignora linhas completamente vazias
            if not any(str(valor or "").strip() for valor in linha.values()):
                continue

            linha = {
                chave.strip(): str(valor or "").strip()
                for chave, valor in linha.items()
                if chave is not None
            }
            alunos.append(linha)

    return alunos, caminho


def converter_nota(valor):
    """Converte a nota para número, aceitando vírgula decimal."""
    valor = str(valor or "").strip()

    if not valor:
        return None

    try:
        nota = float(valor.replace(",", "."))
    except ValueError:
        return None

    if not 0 <= nota <= 10:
        return None

    return nota


def consultar_aluno(aluno):
    """Mostra as notas, a média e a situação do aluno."""
    print("\n" + "=" * 42)
    print("          RESULTADO DO ALUNO")
    print("=" * 42)

    print(f"Nome: {aluno['Nome']}")
    print(f"RA:   {aluno['RA']}")

    notas = {}

    for coluna in COLUNAS_NOTAS:
        nota = converter_nota(aluno.get(coluna, ""))

        if nota is None:
            print(f"{coluna}: Não informada ou inválida")
        else:
            print(f"{coluna}: {nota:.2f}")
            notas[coluna] = nota

    print("-" * 42)

    if len(notas) != len(COLUNAS_NOTAS):
        print("Média final: Não calculada")
        print("Situação: PENDENTE - faltam notas válidas")
    else:
        media = sum(notas.values()) / len(COLUNAS_NOTAS)

        print(f"Média final: {media:.2f}")

        if media >= MEDIA_MINIMA:
            print("Situação: APROVADO")
        else:
            print("Situação: REPROVADO")

    print("=" * 42)


def pesquisar_aluno(alunos):
    """Pesquisa por RA exato ou por parte do nome."""
    busca = input("\nDigite o nome ou RA do aluno: ").strip()

    if not busca:
        print("Digite um nome ou RA válido.")
        return

    busca_normalizada = normalizar(busca)

    encontrados = [
        aluno
        for aluno in alunos
        if normalizar(aluno.get("RA", "")) == busca_normalizada
        or busca_normalizada in normalizar(aluno.get("Nome", ""))
    ]

    if not encontrados:
        print("\nNenhum aluno encontrado.")
        return

    print(f"\nAlunos encontrados: {len(encontrados)}")

    for aluno in encontrados:
        consultar_aluno(aluno)


def main():
    try:
        alunos, caminho = carregar_alunos()
    except (OSError, ValueError) as erro:
        print(f"\nErro ao carregar os dados: {erro}")
        return

    print("=" * 42)
    print("           ROBÔ DE CONSULTA")
    print("=" * 42)
    print(f"Arquivo utilizado: {caminho}")
    print(f"Total de alunos carregados: {len(alunos)}")

    while True:
        print("\n1. Consultar aluno por nome ou RA")
        print("2. Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            pesquisar_aluno(alunos)
        elif opcao == "2":
            print("\nRobô encerrado.")
            break
        else:
            print("Opção inválida. Escolha 1 ou 2.")


if __name__ == "__main__":
    main()

