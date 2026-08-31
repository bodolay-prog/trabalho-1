#!/bin/bash
# Roda o experimento com varias configuracoes de nucleos (via taskset) e grava
# TUDO num unico log CSV, com uma coluna extra "nucleos" (quantidade de nucleos
# usados naquela execucao) para permitir comparacao direta no mesmo arquivo.
#
# Uso: ./run_comparativo.sh [numero_de_execucoes] [saida.log] [config1] [config2] ...
#
# Cada "config" e uma lista de nucleos separada por virgula para o taskset -c,
# ex: "0" (1 nucleo), "0,1" (2 nucleos), "0,1,2,3" (4 nucleos).
#
# Exemplo (Codespace de 4 nucleos, comparando 1 / 2 / 4 nucleos):
#   ./run_comparativo.sh 300 resultados_comparativo.log 0 0,1 0,1,2,3

REPETICOES="${1:-300}"
SAIDA="${2:-resultados_comparativo.log}"
shift 2
CONFIGS=("$@")

if [ ${#CONFIGS[@]} -eq 0 ]; then
    CONFIGS=("0" "0,1" "0,1,2,3")
fi

> "$SAIDA"

for cfg in "${CONFIGS[@]}"; do
    n_nucleos=$(($(echo "$cfg" | tr -cd ',' | wc -c) + 1))
    echo "=== Configuracao: nucleos=$cfg (n=$n_nucleos) ==="
    for ((run=0; run<REPETICOES; run++)); do
        # cada linha original ganha uma coluna extra no final: n_nucleos
        taskset -c "$cfg" ./main-tester "$run" | awk -v n="$n_nucleos" -F',' 'BEGIN{OFS=","} {print $0, n}' >> "$SAIDA"
    done
    echo "  ok."
done

echo "Concluido. $(wc -l < "$SAIDA") linhas em $SAIDA"
