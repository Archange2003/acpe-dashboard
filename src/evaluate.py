"""
Hackathon IndabaX Congo 2026 - Évaluation
==========================================
Compare les recommandations générées par le moteur d'appariement au fichier
de vérité terrain (Appariement_Demandeurs_Offres.xlsx, 3 offres pertinentes
par candidat) et calcule Precision@K, Recall@K, NDCG@K (K=5, K=10).
"""

import numpy as np
import pandas as pd

import os
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")


def dcg_at_k(relevances):
    relevances = np.asarray(relevances, dtype=float)
    discounts = np.log2(np.arange(2, len(relevances) + 2))
    return np.sum(relevances / discounts)


def evaluate(reco: pd.DataFrame, gt: pd.DataFrame, k: int) -> dict:
    gt_map = {
        row.id_demandeur: {row.id_offre1, row.id_offre2, row.id_offre3}
        for row in gt.itertuples()
    }

    reco_k = reco[reco["rank"] <= k].sort_values(["candidate_id", "rank"])
    precisions, recalls, ndcgs = [], [], []

    for cid, group in reco_k.groupby("candidate_id", sort=False):
        relevant = gt_map.get(cid)
        if not relevant:
            continue
        recommended = list(group.sort_values("rank")["job_id"])
        hits = [1 if j in relevant else 0 for j in recommended]

        n_hits = sum(hits)
        precisions.append(n_hits / k)
        recalls.append(n_hits / len(relevant))

        dcg = dcg_at_k(hits)
        ideal_hits = [1] * min(len(relevant), k) + [0] * max(0, k - len(relevant))
        idcg = dcg_at_k(ideal_hits)
        ndcgs.append(dcg / idcg if idcg > 0 else 0.0)

    return {
        f"Precision@{k}": float(np.mean(precisions)),
        f"Recall@{k}": float(np.mean(recalls)),
        f"NDCG@{k}": float(np.mean(ndcgs)),
        "n_candidats_evalues": len(precisions),
    }


def main():
    reco = pd.read_csv(f"{OUT_DIR}/recommandations_top10.csv")
    gt = pd.read_parquet(f"{OUT_DIR}/ground_truth.parquet")

    results = {}
    for k in (5, 10):
        results.update(evaluate(reco, gt, k))

    print("=== Résultats d'évaluation du moteur d'appariement ===")
    for k, v in results.items():
        if isinstance(v, float):
            print(f"  {k:20s}: {v:.4f}")
        else:
            print(f"  {k:20s}: {v}")

    pd.Series(results).to_csv(f"{OUT_DIR}/evaluation_metrics.csv", header=["valeur"])


if __name__ == "__main__":
    main()
