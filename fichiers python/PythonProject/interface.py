# ============================================================
# interface.py — Interface graphique Tkinter (2 onglets)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from graphique import resoudre_graphique, creer_figure
from simplexe  import resoudre_simplexe, formater_resultats_simplexe, exporter_resultats
from calculs   import (
    NOMS_VARS_GRAPHIQUE, NOMS_VARS_SIMPLEXE,
    COEFF_OBJECTIF_GRAPH, COEFF_OBJECTIF_SIMPLEX,
    CONTRAINTES_GRAPHIQUE, CONTRAINTES_SIMPLEXE,
    TYPE_OPTIMISATION, UNITE_OBJECTIF,
)

COULEUR_BG      = "#F4F6F9"
COULEUR_TITRE   = "#2C3E50"
COULEUR_BTN     = "#2980B9"
COULEUR_BTN_TXT = "white"
COULEUR_EXPORT  = "#27AE60"
POLICE_TITRE    = ("Helvetica", 14, "bold")
POLICE_NORMALE  = ("Helvetica", 10)
POLICE_MONO     = ("Courier", 10)


class AppPL(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Optimisation alimentation — Club sportif | PL")
        self.geometry("1050x680")
        self.configure(bg=COULEUR_BG)
        self.resizable(True, True)

        self._res_graph   = None
        self._z_graph     = None
        self._res_simplex = None
        self._canvas_fig  = None

        self._construire_interface()

    def _construire_interface(self):
        header = tk.Frame(self, bg=COULEUR_TITRE, pady=8)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Optimisation de l'alimentation d'un athlete",
            font=("Helvetica", 16, "bold"),
            bg=COULEUR_TITRE, fg="white",
        ).pack()
        tk.Label(
            header,
            text=f"Programmation Lineaire | {TYPE_OPTIMISATION.upper()}IMISATION — {UNITE_OBJECTIF}",
            font=POLICE_NORMALE,
            bg=COULEUR_TITRE, fg="#BDC3C7",
        ).pack()

        style = ttk.Style(self)
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=[12, 4])
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=10)

        self._onglet_graphique(notebook)
        self._onglet_simplexe(notebook)

        self._status_var = tk.StringVar(value="Pret.")
        tk.Label(
            self, textvariable=self._status_var,
            bg="#ECF0F1", anchor="w", relief="sunken",
            font=("Helvetica", 9), padx=6,
        ).pack(fill="x", side="bottom")

    def _onglet_graphique(self, notebook):
        frame = tk.Frame(notebook, bg=COULEUR_BG)
        notebook.add(frame, text="  Methode Graphique  ")

        gauche = tk.Frame(frame, bg=COULEUR_BG, width=260)
        gauche.pack(side="left", fill="y", padx=10, pady=10)
        gauche.pack_propagate(False)

        tk.Label(gauche, text="Donnees du probleme",
                 font=POLICE_TITRE, bg=COULEUR_BG, fg=COULEUR_TITRE).pack(anchor="w", pady=(0, 4))

        self._zone_info_graph = tk.Text(
            gauche, height=16, font=POLICE_MONO, bg="#FDFEFE",
            relief="groove", bd=1, wrap="word",
        )
        self._zone_info_graph.insert("1.0", self._texte_donnees_graphique())
        self._zone_info_graph.configure(state="disabled")
        self._zone_info_graph.pack(fill="x", pady=4)

        tk.Label(gauche, text="Resultat :",
                 font=("Helvetica", 10, "bold"), bg=COULEUR_BG).pack(anchor="w", pady=(8, 0))
        self._res_var_graph = tk.StringVar(value="—")
        tk.Label(gauche, textvariable=self._res_var_graph,
                 font=POLICE_MONO, bg="#EBF5FB",
                 relief="groove", justify="left", padx=6, pady=4,
                 wraplength=230).pack(fill="x")

        self._btn(gauche, "Calculer & Afficher", self._action_graphique,
                  COULEUR_BTN).pack(fill="x", pady=(10, 4))
        self._btn(gauche, "Exporter resultats", self._action_exporter,
                  COULEUR_EXPORT).pack(fill="x")

        self._frame_plot = tk.Frame(frame, bg=COULEUR_BG)
        self._frame_plot.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)

    def _texte_donnees_graphique(self):
        lines = ["Variables :\n"]
        for i, n in enumerate(NOMS_VARS_GRAPHIQUE):
            lines.append(f"  x{i+1} = {n}\n")
        lines.append(f"\nObjectif ({TYPE_OPTIMISATION.upper()}) :\n  Z = ")
        lines.append(" + ".join(f"{c}x{i+1}" for i, c in enumerate(COEFF_OBJECTIF_GRAPH)))
        lines.append("\n\nContraintes :\n")
        for c in CONTRAINTES_GRAPHIQUE:
            expr = " + ".join(f"{a}x{i+1}" for i, a in enumerate(c["coeffs"]))
            lines.append(f"  {expr} <= {c['rhs']}\n  [{c['label']}]\n")
        return "".join(lines)

    def _action_graphique(self):
        self._status("Calcul en cours...")
        self.update_idletasks()
        try:
            sol, z, sommets, infos = resoudre_graphique()
            self._res_graph = sol
            self._z_graph   = z

            if sol is None:
                messagebox.showerror("Erreur", "Probleme sans solution realisable.")
                self._status("Pas de solution.")
                return

            lignes = []
            for nom, v in zip(NOMS_VARS_GRAPHIQUE, sol):
                lignes.append(f"{nom} = {v:.4f}")
            lignes.append(f"Z* = {z:.4f} {UNITE_OBJECTIF}")
            lignes.append("\nContraintes :")
            for dc in infos:
                etat = "Saturee" if dc["saturee"] else "Active"
                lignes.append(f"  {dc['label']}: {dc['valeur']:.2f}/{dc['rhs']}  {etat}")
            self._res_var_graph.set("\n".join(lignes))

            fig = creer_figure(sol, z, sommets)
            self._afficher_figure(fig, self._frame_plot)
            self._status(f"Solution optimale : Z* = {z:.4f} {UNITE_OBJECTIF}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self._status(f"Erreur : {e}")

    def _afficher_figure(self, fig, parent):
        for widget in parent.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas_fig = canvas

    def _onglet_simplexe(self, notebook):
        frame = tk.Frame(notebook, bg=COULEUR_BG)
        notebook.add(frame, text="  Methode Simplexe  ")

        barre = tk.Frame(frame, bg=COULEUR_BG)
        barre.pack(fill="x", padx=10, pady=(10, 4))
        self._btn(barre, "Resoudre (Simplexe)", self._action_simplexe,
                  COULEUR_BTN).pack(side="left", padx=4)
        self._btn(barre, "Exporter resultats", self._action_exporter,
                  COULEUR_EXPORT).pack(side="left", padx=4)
        self._btn(barre, "Effacer", self._effacer_simplexe,
                  "#7F8C8D").pack(side="left", padx=4)

        txt_frame = tk.Frame(frame, bg=COULEUR_BG)
        txt_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(txt_frame)
        scrollbar.pack(side="right", fill="y")

        self._zone_simplexe = tk.Text(
            txt_frame, font=POLICE_MONO, bg="#FDFEFE",
            relief="groove", bd=1, wrap="none",
            yscrollcommand=scrollbar.set,
            state="disabled",
        )
        self._zone_simplexe.pack(fill="both", expand=True)
        scrollbar.config(command=self._zone_simplexe.yview)

        self._zone_simplexe.tag_config("titre",   foreground="#1A5276",
                                        font=("Courier", 10, "bold"))
        self._zone_simplexe.tag_config("succes",  foreground="#1E8449")
        self._zone_simplexe.tag_config("saturee", foreground="#1E8449",
                                        font=("Courier", 10, "bold"))
        self._zone_simplexe.tag_config("normal",  foreground="#2C3E50")

        self._ecrire_simplexe(
            "  Cliquez sur 'Resoudre (Simplexe)' pour lancer le calcul.\n\n"
            f"  Variables ({len(NOMS_VARS_SIMPLEXE)}) : "
            + ", ".join(NOMS_VARS_SIMPLEXE) + "\n"
            f"  Contraintes ({len(CONTRAINTES_SIMPLEXE)}) : "
            + ", ".join(c["label"] for c in CONTRAINTES_SIMPLEXE) + "\n",
            tag="titre",
        )

    def _action_simplexe(self):
        self._status("Calcul Simplexe en cours...")
        self.update_idletasks()
        try:
            res = resoudre_simplexe()
            self._res_simplex = res
            texte = formater_resultats_simplexe(res)

            self._zone_simplexe.configure(state="normal")
            self._zone_simplexe.delete("1.0", "end")
            for ligne in texte.split("\n"):
                if "Saturee" in ligne:
                    self._zone_simplexe.insert("end", ligne + "\n", "saturee")
                elif ligne.startswith("=") or ligne.startswith("-"):
                    self._zone_simplexe.insert("end", ligne + "\n", "titre")
                elif "Z*" in ligne or "Optimale" in ligne:
                    self._zone_simplexe.insert("end", ligne + "\n", "succes")
                else:
                    self._zone_simplexe.insert("end", ligne + "\n", "normal")
            self._zone_simplexe.configure(state="disabled")

            if res["succes"]:
                self._status(f"Simplexe resolu : Z* = {res['valeur_z']:.4f} {UNITE_OBJECTIF}")
            else:
                self._status("Pas de solution.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self._status(f"Erreur : {e}")

    def _effacer_simplexe(self):
        self._zone_simplexe.configure(state="normal")
        self._zone_simplexe.delete("1.0", "end")
        self._zone_simplexe.configure(state="disabled")
        self._status("Zone effacee.")

    def _action_exporter(self):
        if self._res_graph is None and self._res_simplex is None:
            messagebox.showwarning("Aucun resultat",
                                   "Calculez d'abord les solutions avant d'exporter.")
            return
        chemin = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichier texte", "*.txt"), ("Tous les fichiers", "*.*")],
            initialfile="resultats_PL.txt",
            title="Enregistrer les resultats",
        )
        if not chemin:
            return
        try:
            exporter_resultats(self._res_graph, self._z_graph,
                               self._res_simplex or {}, chemin)
            messagebox.showinfo("Export reussi", f"Resultats enregistres :\n{chemin}")
            self._status(f"Exporte -> {chemin}")
        except Exception as e:
            messagebox.showerror("Erreur export", str(e))

    def _btn(self, parent, texte, commande, couleur):
        return tk.Button(
            parent, text=texte, command=commande,
            bg=couleur, fg=COULEUR_BTN_TXT,
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=8, pady=5, cursor="hand2",
            activebackground=couleur, activeforeground="white",
        )

    def _ecrire_simplexe(self, texte, tag="normal"):
        self._zone_simplexe.configure(state="normal")
        self._zone_simplexe.insert("end", texte, tag)
        self._zone_simplexe.configure(state="disabled")

    def _status(self, msg):
        self._status_var.set(msg)
        self.update_idletasks()