"""
Analisa o log bruto gerado por exp4 / run_experimentos.sh / run_comparativo.sh.

Formato de cada linha (a coluna final "nucleos" e OPCIONAL, so aparece se voce
usou o run_comparativo.sh):
  FILHO,run_id,indice_criacao,pid,tempo_ms[,nucleos]
  WAIT,run_id,rank_termino,indice_criacao,pid,tempo_ms[,nucleos]

Se a coluna "nucleos" estiver presente, o script automaticamente separa a
analise por configuracao de nucleos e gera um grafico comparativo.

Uso: python3 analisar.py resultados.log
"""
import sys
import csv
import numpy as np
import pandas as pd
from scipy.stats import kendalltau
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def carregar(caminho):
    filhos, waits = [], []
    tem_nucleos = None
    with open(caminho, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            if row[0] == "FILHO":
                if tem_nucleos is None:
                    tem_nucleos = len(row) == 6
                if tem_nucleos:
                    _, run_id, idx, pid, t, nuc = row
                    filhos.append((int(run_id), int(idx), int(pid), float(t), int(nuc)))
                else:
                    _, run_id, idx, pid, t = row
                    filhos.append((int(run_id), int(idx), int(pid), float(t), None))
            elif row[0] == "WAIT":
                if tem_nucleos is None:
                    tem_nucleos = len(row) == 7
                if tem_nucleos:
                    _, run_id, rank, idx, pid, t, nuc = row
                    waits.append((int(run_id), int(rank), int(idx), int(pid), float(t), int(nuc)))
                else:
                    _, run_id, rank, idx, pid, t = row
                    waits.append((int(run_id), int(rank), int(idx), int(pid), float(t), None))
    cols_f = ["run", "idx_criacao", "pid", "t_fim_ms", "nucleos"]
    cols_w = ["run", "rank_termino", "idx_criacao", "pid", "t_wait_ms", "nucleos"]
    df_filhos = pd.DataFrame(filhos, columns=cols_f)
    df_waits = pd.DataFrame(waits, columns=cols_w)
    # Se nao houver coluna nucleos de verdade, trata tudo como um unico grupo.
    if df_waits["nucleos"].isna().all():
        df_filhos["nucleos"] = "unico"
        df_waits["nucleos"] = "unico"
    return df_filhos, df_waits


def analisar_grupo(df_filhos, df_waits, rotulo):
    n_execucoes = df_waits["run"].nunique()
    N = df_waits["idx_criacao"].nunique()
    print(f"\n########## Configuracao: {rotulo} ##########")
    print(f"Execucoes: {n_execucoes} | Filhos por execucao (N): {N}")

    # Taxa de inversao entre pares consecutivos
    inversoes = {}
    for run_id, grupo in df_waits.groupby("run"):
        ordem = grupo.sort_values("idx_criacao")["rank_termino"].values
        for i in range(N - 1):
            inversoes.setdefault((i, i + 1), []).append(ordem[i] > ordem[i + 1])
    taxa_media = np.mean([np.mean(v) for v in inversoes.values()])

    # Kendall's tau por execucao
    taus = []
    for run_id, grupo in df_waits.groupby("run"):
        g = grupo.sort_values("idx_criacao")
        tau, _ = kendalltau(g["idx_criacao"].values, g["rank_termino"].values)
        taus.append(tau)
    taus = np.array(taus)

    print(f"  Taxa media de inversao (pares consecutivos): {taxa_media*100:.1f}%")
    print(f"  Kendall's tau: media={taus.mean():.3f}  desvio-padrao={taus.std(ddof=1):.3f}")
    print(f"  % execucoes com tau=1.0 (ordem perfeitamente preservada): {np.mean(taus==1.0)*100:.1f}%")

    return {
        "rotulo": rotulo,
        "n_execucoes": n_execucoes,
        "taxa_inversao_media": taxa_media,
        "tau_medio": taus.mean(),
        "tau_std": taus.std(ddof=1),
        "pct_tau_perfeito": np.mean(taus == 1.0),
        "taus": taus,
    }


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "resultados_brutos.log"
    df_filhos, df_waits = carregar(caminho)

    grupos = sorted(df_waits["nucleos"].unique(), key=lambda x: (str(x)))
    resumo = []
    for g in grupos:
        resumo.append(analisar_grupo(
            df_filhos[df_filhos["nucleos"] == g],
            df_waits[df_waits["nucleos"] == g],
            rotulo=f"{g} nucleo(s)" if g != "unico" else "execucao unica (sem comparacao)"
        ))

    # --- Grafico comparativo --------------------------------------------------
    if len(resumo) > 1:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        rotulos = [r["rotulo"] for r in resumo]

        axes[0].bar(rotulos, [r["taxa_inversao_media"] * 100 for r in resumo])
        axes[0].set_ylabel("Taxa media de inversao (%)")
        axes[0].set_title("Inversao de ordem vs. nucleos disponiveis")
        axes[0].tick_params(axis="x", rotation=20)

        axes[1].boxplot([r["taus"] for r in resumo], labels=rotulos)
        axes[1].set_ylabel("Kendall's tau por execucao")
        axes[1].set_title("Correlacao de ordem vs. nucleos disponiveis")
        axes[1].tick_params(axis="x", rotation=20)

        plt.tight_layout()
        plt.savefig("comparativo_nucleos.png", dpi=150)
        print("Grafico comparativo salvo em comparativo_nucleos.png")
    else:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.hist(resumo[0]["taus"], bins=np.arange(-1.0, 1.05, 0.1), edgecolor="black")
        ax.set_xlabel("Kendall's tau")
        ax.set_ylabel("Numero de execucoes")
        plt.tight_layout()
        plt.savefig("analise_resultados.png", dpi=150)
        print("Grafico salvo em analise_resultados.png")


if __name__ == "__main__":
    main()
