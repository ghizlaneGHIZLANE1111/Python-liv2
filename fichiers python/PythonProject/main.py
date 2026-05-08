# ============================================================
# main.py — Point d'entree
# Lancement : python main.py
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from interface import AppPL
def main():
    app = AppPL()
    app.mainloop()

if __name__ == "__main__":
    main()
