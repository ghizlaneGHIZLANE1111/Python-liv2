# ============================================================
# calculs.py — Données du problème (selon rapport)
# Projet : Optimisation alimentation athlète — Club sportif
# ============================================================

# ─────────────────────────────────────────────────────────────
# 1. NOMS DES VARIABLES
# ─────────────────────────────────────────────────────────────
NOMS_VARS_GRAPHIQUE = ["Legumes x1 (kg)", "Poulet x2 (kg)"]

NOMS_VARS_SIMPLEXE = [
    "Legumes y1 (kg)",
    "Poulet y2 (kg)",
    "Fecutents y3 (kg)",
    "Fruits y4 (kg)"
]

# ─────────────────────────────────────────────────────────────
# 2. FONCTION OBJECTIF  →  Min Z = 2x1 + 4x2  (Chapitre 1)
#                          Min W = 2y1 + 4y2 + 3y3 + 5y4  (Chapitre 2)
# ─────────────────────────────────────────────────────────────
COEFF_OBJECTIF_GRAPH   = [2, 4]
COEFF_OBJECTIF_SIMPLEX = [2, 4, 3, 5]
TYPE_OPTIMISATION      = "min"

# ─────────────────────────────────────────────────────────────
# 3. CONTRAINTES GRAPHIQUE (contraintes >= converties en <=)
#    ex: 20x1 + 10x2 >= 60  devient  -20x1 - 10x2 <= -60
# ─────────────────────────────────────────────────────────────
CONTRAINTES_GRAPHIQUE = [
    {"coeffs": [-20, -10], "rhs": -60, "label": "Calories >= 60"},
    {"coeffs": [-5,  -20], "rhs": -40, "label": "Proteines >= 40"},
    {"coeffs": [-1,   -1], "rhs":  -5, "label": "Quantite >= 5"},
]

# ─────────────────────────────────────────────────────────────
# 4. CONTRAINTES SIMPLEXE (4 variables, meme conversion)
# ─────────────────────────────────────────────────────────────
CONTRAINTES_SIMPLEXE = [
    {"coeffs": [-20, -10, -15, -25], "rhs": -60, "label": "Calories >= 60"},
    {"coeffs": [-5,  -20, -10,  -8], "rhs": -40, "label": "Proteines >= 40"},
    {"coeffs": [-1,   -1,  -1,  -1], "rhs":  -5, "label": "Quantite >= 5"},
]

# ─────────────────────────────────────────────────────────────
# 5. UNITES
# ─────────────────────────────────────────────────────────────
UNITE_OBJECTIF = "DH"
UNITE_VARS     = "kg"


# ─────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────

def evaluer_objectif(solution, coeffs):
    return sum(c * x for c, x in zip(coeffs, solution))

def verifier_contrainte(solution, contrainte):
    valeur = sum(a * x for a, x in zip(contrainte["coeffs"], solution))
    return valeur <= contrainte["rhs"] + 1e-9

def contrainte_saturee(solution, contrainte, tol=1e-6):
    valeur = sum(a * x for a, x in zip(contrainte["coeffs"], solution))
    return abs(valeur - contrainte["rhs"]) <= tol