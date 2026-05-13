"""Ponto de entrada: python main.py  |  python main.py fase3  (inicia directo nessa fase)"""

import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().lstrip("-")
        if arg in ("fase1", "fase2", "fase3"):
            import tour_teresina_golf.config as _cfg

            _cfg.START_LEVEL_ID = arg
    from tour_teresina_golf.app import main

    main()
