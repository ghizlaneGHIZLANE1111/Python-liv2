# ============================================================
# simplexe.py — Méthode du Simplexe (4 variables)
# ============================================================

from scipy.optimize import linprog

from calculs import (
    CONTRAINTES_SIMPLEXE,
    COEFF_OBJECTIF_SIMPLEX,
    NOMS_VARS_SIMPLEXE,
    TYPE_OPTIMISATION,
    UNITE_OBJECTIF,
    UNITE_VARS,
    evaluer_objectif,
    contrainte_saturee,
)


def resoudre_simplexe():
    A  = [c["coeffs"] for c in CONTRAINTES_SIMPLEXE]
    b  = [c["rhs"]    for c in CONTRAINTES_SIMPLEXE]
    n  = len(COEFF_OBJECTIF_SIMPLEX)
    c  = (COEFF_OBJECTIF_SIMPLEX if TYPE_OPTIMISATION == "min"
          else [-v for v in COEFF_OBJECTIF_SIMPLEX])

    bounds = [(0, None)] * n
    res    = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

    if res.status != 0:
        return {"succes": False, "message": res.message}

    sol = list(res.x)
    z   = evaluer_objectif(sol, COEFF_OBJECTIF_SIMPLEX)

    details_contraintes = []
    for i, cont in enumerate(CONTRAINTES_SIMPLEXE):
        utilise = sum(a * x for a, x in zip(cont["coeffs"], sol))
        reste   = cont["rhs"] - utilise
        sature  = contrainte_saturee(sol, cont)
        details_contraintes.append({
            "index":   i + 1,
            "label":   cont["label"],
            "utilise": utilise,
            "rhs":     cont["rhs"],
            "reste":   reste,
            "saturee": sature,
        })

    var_ecart = {
        f"s{i+1} ({cont['label']})": cont["rhs"] - sum(
            a * x for a, x in zip(cont["coeffs"], sol)
        )
        for i, cont in enumerate(CONTRAINTES_SIMPLEXE)
    }

    return {
        "succes":              True,
        "solution":            sol,
        "valeur_z":            z,
        "details_contraintes": details_contraintes,
        "var_ecart":           var_ecart,
        "nb_iterations":       getattr(res, "nit", "N/A"),
    }


def formater_resultats_simplexe(res):
    if not res.get("succes"):
        return f"Echec de la resolution : {res.get('message', '?')}"

    lines = []
    lines.append("=" * 58)
    lines.append("  RESULTATS — METHODE DU SIMPLEXE")
    lines.append("  Optimisation alimentation athlete (Club sportif)")
    lines.append("=" * 58)

    lines.append("\nSOLUTION OPTIMALE")
    lines.append("-" * 40)
    for nom, val in zip(NOMS_VARS_SIMPLEXE, res["solution"]):
        lines.append(f"  {nom:<25} = {val:>8.4f} {UNITE_VARS}")

    opt_type = "Minimale" if TYPE_OPTIMISATION == "min" else "Maximale"
    lines.append(f"\n  Valeur {opt_type} Z* = {res['valeur_z']:.4f} {UNITE_OBJECTIF}")
    lines.append(f"  Nombre d'iterations   : {res['nb_iterations']}")

    lines.append("\nANALYSE DES CONTRAINTES")
    lines.append("-" * 58)
    lines.append(f"  {'N':<4} {'Contrainte':<22} {'Utilise':>8} {'Limite':>8} {'Reste':>8}  {'Etat'}")
    lines.append("  " + "-" * 54)
    for dc in res["details_contraintes"]:
        etat = "Saturee" if dc["saturee"] else "Active"
        lines.append(
            f"  {dc['index']:<4} {dc['label']:<22} "
            f"{dc['utilise']:>8.2f} {dc['rhs']:>8.2f} {dc['reste']:>8.2f}  {etat}"
        )

    lines.append("\nVARIABLES D'ECART (ressources inutilisees)")
    lines.append("-" * 40)
    for nom, val in res["var_ecart"].items():
        lines.append(f"  {nom:<35} = {val:>8.4f}")

    lines.append("\n" + "=" * 58)
    return "\n".join(lines)


def exporter_resultats(res_graph, z_graph, res_simplex, chemin="resultats_PL.txt"):
    from calculs import CONTRAINTES_GRAPHIQUE, COEFF_OBJECTIF_GRAPH, NOMS_VARS_GRAPHIQUE

    with open(chemin, "w", encoding="utf-8") as f:
        f.write("=" * 62 + "\n")
        f.write("  RAPPORT — PROGRAMMATION LINEAIRE\n")
        f.write("  Optimisation alimentation pour un athlete\n")
        f.write("  Club sportif\n")
        f.write("=" * 62 + "\n\n")

        f.write("-" * 62 + "\n")
        f.write("  1. METHODE GRAPHIQUE (2 variables)\n")
        f.write("-" * 62 + "\n")
        f.write(f"  Variables : {', '.join(NOMS_VARS_GRAPHIQUE)}\n")
        f.write("  Fonction objectif : Z = ")
        f.write(" + ".join(f"{c}*x{i+1}" for i, c in enumerate(COEFF_OBJECTIF_GRAPH)))
        f.write(f"  ({TYPE_OPTIMISATION.upper()})\n\n")
        f.write("  Contraintes :\n")
        for c in CONTRAINTES_GRAPHIQUE:
            expr = " + ".join(f"{a}*x{i+1}" for i, a in enumerate(c["coeffs"]))
            f.write(f"    {expr} <= {c['rhs']}  [{c['label']}]\n")

        if res_graph is not None:
            f.write(f"\n  Solution optimale :\n")
            for nom, val in zip(NOMS_VARS_GRAPHIQUE, res_graph):
                f.write(f"    {nom} = {val:.4f} {UNITE_VARS}\n")
            f.write(f"    Z* = {z_graph:.4f} {UNITE_OBJECTIF}\n")
        else:
            f.write("  Aucune solution realisable trouvee.\n")

        f.write("\n" + "-" * 62 + "\n")
        f.write("  2. METHODE DU SIMPLEXE (4 variables)\n")
        f.write("-" * 62 + "\n")
        f.write(formater_resultats_simplexe(res_simplex))
        f.write("\n")

    return chemin