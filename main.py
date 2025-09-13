import sys
import os
import argparse
import pygame
from projekt.config import *
from projekt.game import Game

sys.path.append(os.path.join(os.path.dirname(__file__), "projekt"))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Donkey Kong AI")

    parser = argparse.ArgumentParser(description="Pokreni igru u različitim modovima")
    parser.add_argument("--mode", type=str, choices=["run", "run_neat", "run_winner", "resume"], default="run_neat",
                        help="Odaberi način rada: run, run_neat, run_winner, resume")
    args = parser.parse_args()

    game = Game(screen)

    if args.mode == "run":
        game.run()
    elif args.mode == "run_neat":
        game.run_neat(game.config_path)
    elif args.mode == "run_winner":
        game.run_winner(game.config_path)
    elif args.mode == "resume":
        game.run_neat(game.config_path, resume=True)

if __name__ == "__main__":
    main()
