# ============================================================
# graphique.py — Méthode graphique (2 variables)
# ============================================================

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scipy.optimize import linprog
from scipy.spatial import ConvexHull

from calculs import (
    CONTRAINTES_GRAPHIQUE,
    COEFF_OBJECTIF_GRAPH,
    NOMS_VARS_GRAPHIQUE,
    TYPE_OPTIMISATION,
    UNITE_OBJECTIF,
    UNITE_VARS,
    evaluer_objectif,
)


def resoudre_graphique():
    A = [c["coeffs"] for c in CONTRAINTES_GRAPHIQUE]
    b = [c["rhs"]    for c in CONTRAINTES_GRAPHIQUE]
    c = COEFF_OBJECTIF_GRAPH if TYPE_OPTIMISATION == "min" else [-v for v in COEFF_OBJECTIF_GRAPH]

    bounds = [(0, None), (0, None)]
    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

    if res.status != 0:
        return None, None, [], []

    sol = list(res.x)
    z   = evaluer_objectif(sol, COEFF_OBJECTIF_GRAPH)
    sommets = _calculer_sommets(A, b)

    infos = []
    for cont in CONTRAINTES_GRAPHIQUE:
        val    = sum(a * x for a, x in zip(cont["coeffs"], sol))
        sature = abs(val - cont["rhs"]) < 1e-6
        infos.append({
            "label":   cont["label"],
            "valeur":  val,
            "rhs":     cont["rhs"],
            "saturee": sature,
        })

    return sol, z, sommets, infos


def _calculer_sommets(A, b):
    pts = [[0, 0]]
    n   = len(A)

    for i in range(n):
        for j in range(i + 1, n):
            try:
                M = np.array([A[i], A[j]], dtype=float)
                r = np.array([b[i], b[j]], dtype=float)
                x = np.linalg.solve(M, r)
                if x[0] >= -1e-9 and x[1] >= -1e-9:
                    pts.append(list(x))
            except np.linalg.LinAlgError:
                pass
        if abs(A[i][1]) > 1e-9:
            pts.append([0, b[i] / A[i][1]])
        if abs(A[i][0]) > 1e-9:
            pts.append([b[i] / A[i][0], 0])

    def est_realisable(p):
        return all(
            sum(A[k][d] * p[d] for d in range(2)) <= b[k] + 1e-9
            for k in range(n)
        ) and p[0] >= -1e-9 and p[1] >= -1e-9

    pts_ok = [p for p in pts if est_realisable(p)]

    if len(pts_ok) < 3:
        return pts_ok

    arr = np.array(pts_ok)
    try:
        hull = ConvexHull(arr)
        return arr[hull.vertices].tolist()
    except Exception:
        return pts_ok


COULEURS_CONTRAINTES = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"]


def creer_figure(sol, z, sommets):
    fig, ax = plt.subplots(figsize=(8, 6))

    xmax = max([c["rhs"] / c["coeffs"][0] for c in CONTRAINTES_GRAPHIQUE
                if abs(c["coeffs"][0]) > 1e-9] + [10]) * 1.15
    ymax = max([c["rhs"] / c["coeffs"][1] for c in CONTRAINTES_GRAPHIQUE
                if abs(c["coeffs"][1]) > 1e-9] + [10]) * 1.15
    x = np.linspace(0, xmax, 400)

    for idx, cont in enumerate(CONTRAINTES_GRAPHIQUE):
        a1, a2 = cont["coeffs"]
        b_rhs  = cont["rhs"]
        color  = COULEURS_CONTRAINTES[idx % len(COULEURS_CONTRAINTES)]
        if abs(a2) > 1e-9:
            y = (b_rhs - a1 * x) / a2
            ax.plot(x, y, color=color, linewidth=2, label=cont["label"])
        elif abs(a1) > 1e-9:
            ax.axvline(b_rhs / a1, color=color, linewidth=2, label=cont["label"])

    if len(sommets) >= 3:
        poly     = np.array(sommets)
        hull_pts = poly[ConvexHull(poly).vertices]
        patch    = plt.Polygon(hull_pts, alpha=0.20, color="#27AE60", label="Region realisable")
        ax.add_patch(patch)

    for sv in sommets:
        ax.plot(sv[0], sv[1], "ko", markersize=5)

    if sol is not None:
        ax.plot(sol[0], sol[1], "r*", markersize=18, zorder=5,
                label=f"Optimum ({sol[0]:.2f}, {sol[1]:.2f})")
        ax.annotate(
            f"Z* = {z:.2f} {UNITE_OBJECTIF}",
            xy=(sol[0], sol[1]),
            xytext=(sol[0] + xmax * 0.05, sol[1] + ymax * 0.05),
            fontsize=10, color="darkred",
            arrowprops={"arrowstyle": "->", "color": "darkred"},
        )

    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xlabel(f"{NOMS_VARS_GRAPHIQUE[0]} ({UNITE_VARS})", fontsize=11)
    ax.set_ylabel(f"{NOMS_VARS_GRAPHIQUE[1]} ({UNITE_VARS})", fontsize=11)
    ax.set_title("Methode Graphique — Optimisation alimentation athlete",
                 fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    return fig