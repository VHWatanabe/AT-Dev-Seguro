import json
import sys

LIMITE_BLOQUEIO = "HIGH"
SEVERIDADES_ORDEM = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


def main():
    caminho_relatorio = sys.argv[1]
    with open(caminho_relatorio) as arquivo:
        dados = json.load(arquivo)

    achados_bloqueantes = [
        resultado
        for resultado in dados.get("results", [])
        if SEVERIDADES_ORDEM.get(resultado["issue_severity"], 0)
        >= SEVERIDADES_ORDEM[LIMITE_BLOQUEIO]
    ]

    if achados_bloqueantes:
        print(f"Pipeline bloqueado: {len(achados_bloqueantes)} achado(s) de severidade Alta ou superior.")
        for achado in achados_bloqueantes:
            print(f"- {achado['test_name']} em {achado['filename']}:{achado['line_number']}")
        sys.exit(1)

    print("Nenhum achado bloqueante. Pipeline segue.")
    sys.exit(0)


if __name__ == "__main__":
    main()