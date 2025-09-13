import pygame
import pygame as py
import random
import os
import neat
import pickle

#from projekt import border
from projekt.super_coin import SuperCoin
from projekt.punishment import Punishment
from projekt.coin import Coin
from projekt.player import Player
from projekt.platformdk import PlatformDK
from projekt.border import Border
from projekt.ladder import Ladder
from projekt.barrel import Barrel
from projekt.ladder_detect import LadderDetect
from projekt.princess import Princess
from projekt.config import *
from projekt.visualizeNEAT import VisualizeNN
import time

MIN_BARREL_SPAWN = 3000
MAX_BARREL_SPAWN = 10000

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.clock = py.time.Clock()

        self.borders = [Border(x, y, width, height) for (x, y, width, height) in Border.border_positions]
        self.platforms = [PlatformDK(x, y, width, height) for (x, y, width, height) in PlatformDK.platform_positions]
        self.ladders = [Ladder(x, y, width, height) for (x, y, width, height) in Ladder.ladder_positions]
        self.ladders_detect = [LadderDetect(x, y, width, height) for (x, y, width, height) in LadderDetect.ladder_detect_positions]

        self.barrels = []
        self.player = Player(PLAYER_X, PLAYER_Y, self.platforms, self.borders, self.ladders, self.ladders_detect)
        self.princess = Princess(PRINCESS_X, PRINCESS_Y, self.player)

        self.level_image = py.image.load(os.path.join('projekt', 'Assets', 'level.png')).convert()

        self.NEW_BARREL_EVENT = py.USEREVENT + 1
        py.time.set_timer(self.NEW_BARREL_EVENT, random.randint(MIN_BARREL_SPAWN, MAX_BARREL_SPAWN))
        self.game_over = False
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.txt')

        self.barrel_remover = py.Rect(10, 710, 50, 50)
        self.neat_visualizer = VisualizeNN(pos=(self.screen_width - 600, self.screen_height - 600),
                                           size=(600, 600), update_interval=30)

        self.max_lifetime = 20

        self.last_jump_time = 0
        self.jump_cooldown = 1.0

        self.dk_pos = (50, 150)

        self.dk_idle = self.load_scaled_image('kong.png', 100, 100)
        self.dk_dance = [
            self.load_scaled_image('kong_left.png', 100, 100),
            self.load_scaled_image('kong_right.png', 100, 100),
        ]
        self.dk_throw = [
            self.load_scaled_image('kong_barrel_left.png', 100, 100),
            self.load_scaled_image('kong_barrel_right.png', 100, 100)
        ]

        self.best_ever_fitness = float("-inf")

        self.dk_mode = 'idle'
        self.dk_frame = 0
        self.dk_counter = 0
        self.dk_timer = 0

        self.throwing = False
        self.throw_frame = 0
        self.throw_counter = 0
        self.throw_delay = 8
        self.pending_barrel = False

    def load_scaled_image(self, filename, width, height):
            path = os.path.join('projekt', 'Assets', filename)
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, (width, height))

    def draw_eval(self, players, neat_img=None, overlay_data=None):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.level_image, (0, 0))

        for platform in self.platforms:
            self.screen.blit(platform.image, platform.rect)
        for borderEval in self.borders:
            self.screen.blit(borderEval.image, borderEval.rect)
        for ladder in self.ladders:
            self.screen.blit(ladder.image, ladder.rect)
        for ladder_detect in self.ladders_detect:
            self.screen.blit(ladder_detect.image, ladder_detect.rect)
        for barrel in self.barrels:
            barrel.draw(self.screen)
        self.princess.draw(self.screen)

        self.coins.draw(self.screen)

        self.scoins.draw(self.screen)


        for player in players:
            player.draw(self.screen)


        if neat_img is not None:
            self.screen.blit(neat_img, (self.screen_width - 600, self.screen_height - 600))
        if overlay_data is not None:
            font = py.font.SysFont("comicsans", 20)
            x_offset = self.screen_width - 300
            y_offset = 10
            lines = [
                f"Gen: {overlay_data['generation']}",
                f"Alive: {overlay_data['alive']}",
                f"Max Fitness: {overlay_data['max_fitness']:.2f}",
                f"Max Lifetime: {overlay_data['max_lifetime']}",
            ]
            for line in lines:
                text_surface = font.render(line, True, WHITE)
                self.screen.blit(text_surface, (x_offset, y_offset))
                y_offset += text_surface.get_height() + 5
        self.draw_thrower()
        py.display.flip()


    def draw(self, neat_img=None, overlay_data=None):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.level_image, (0, 0))
        for platform in self.platforms:
            self.screen.blit(platform.image, platform.rect)
        for borderEval in self.borders:
            self.screen.blit(borderEval.image, borderEval.rect)
        for ladder in self.ladders:
            self.screen.blit(ladder.image, ladder.rect)
        for ladder_detect in self.ladders_detect:
            self.screen.blit(ladder_detect.image, ladder_detect.rect)
        for barrel in self.barrels:
            barrel.draw(self.screen)


        self.princess.draw(self.screen)

        if self.player is not None:
            self.player.draw(self.screen)
        if neat_img is not None:
            self.screen.blit(neat_img, (self.screen_width - 600, self.screen_height - 600))
        self.draw_thrower()
        py.display.flip()

    def update_thrower(self):
        if self.dk_mode == 'idle':
            self.dk_timer += 1
            if self.dk_timer > 300:
                self.dk_mode = 'nudge'
                self.dk_frame = 0
                self.dk_counter = 0
                self.dk_timer = 0

        elif self.dk_mode == 'nudge':
            self.dk_counter += 1
            if self.dk_counter >= 15:
                self.dk_counter = 0
                self.dk_frame += 1
                if self.dk_frame >= len(self.dk_dance):
                    self.dk_mode = 'idle'
                    self.dk_frame = 0

        elif self.dk_mode == 'prethrow':
            self.dk_counter += 1
            if self.dk_counter >= 8:
                self.dk_counter = 0
                self.dk_frame += 1
                if self.dk_frame >= len(self.dk_throw):
                    self.dk_mode = 'idle'
                    self.dk_frame = 0

    def draw_thrower(self):
        if self.dk_mode == 'nudge':
            img = self.dk_dance[self.dk_frame]
        elif self.dk_mode == 'prethrow':
            img = self.dk_throw[self.dk_frame]
        else:
            img = self.dk_idle

        self.screen.blit(img, self.dk_pos)

    def update(self):
        keys = py.key.get_pressed()
        if self.player is not None:
            self.player.update_player(keys, self.platforms)
            if self.player.rect.colliderect(self.princess.rect):
                self.player = None
        for barrel in self.barrels:
            barrel.update_barrel()
            if self.player and self.player.rect.colliderect(barrel.rect):
                print("Game over.")
                self.game_over = True

        for barrel in self.barrels[:]:
            if barrel.rect.colliderect(self.barrel_remover):
                self.barrels.remove(barrel)
        self.update_thrower()

    def run_neat(self, config_path, generations=10000, simulation_frames=3000, resume = False):
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path)
        p = neat.Population(config)
        p.add_reporter(neat.StdOutReporter(True))
        p.add_reporter(neat.StatisticsReporter())

        gen = 0

        if not py.get_init():
            py.init()
        if not py.display.get_init() or py.display.get_surface() is None:
            py.display.set_mode((self.screen_width, self.screen_height))


        if resume:
            checkpoints = [f for f in os.listdir() if f.startswith("dk-checkpoint-")]
            if checkpoints:
                last = sorted(checkpoints, key=lambda x: int(x.split("-")[-1]))[-1]
                print(f"✱ Obnavljam iz {last}")
                p = neat.Checkpointer.restore_checkpoint(last)
            else:
                print("✱ Nije pronađen nijedan checkpoint – krećem ispočetka.")
                p = neat.Population(config)
        else:
            p = neat.Population(config)

        p.add_reporter(neat.StdOutReporter(True))
        p.add_reporter(neat.StatisticsReporter())

        p.add_reporter(
            neat.Checkpointer(generation_interval=10,
                              filename_prefix="dk-checkpoint-")
        )

        def eval_genomes(genomes, config):
            nonlocal gen
            gen += 1

            if gen % 5 == 0:
                self.max_lifetime += 5

            max_frames = self.max_lifetime * FPS

            self.barrels = []
            nets = []
            players = []
            ge = []

            last_positions = []
            stuck_counter = []

            self.coins = pygame.sprite.Group()
            for (x, y, width, height) in Coin.coin_positions:
                coin = Coin(x, y, width, height)
                self.coins.add(coin)

            self.scoins = pygame.sprite.Group()
            for (x, y, width, height) in SuperCoin.scoin_positions:
                scoin = SuperCoin(x, y, width, height)
                self.scoins.add(scoin)

            for genome_id, genome in genomes:
                genome.fitness = 0
                net = neat.nn.FeedForwardNetwork.create(genome, config)
                nets.append(net)
                p_inst = Player(PLAYER_X, PLAYER_Y, self.platforms, self.borders, self.ladders, self.ladders_detect)
                p_inst.best_y = p_inst.rect.y
                players.append(p_inst)
                ge.append(genome)
                last_positions.append(p_inst.rect.x)
                stuck_counter.append(0)

                p_inst.was_grounded = True
                p_inst.has_jumped = False
                p_inst.previous_best_y = p_inst.rect.y
                p_inst.frames_since_jump = 0
                p_inst.jump_rewarded = False

            frame = 0
            neat_viz_surface = None

            while frame < max_frames and players:
                for event in self._safe_get_events():
                    if event.type == py.QUIT:
                        py.quit()
                        exit()
                    elif event.type == self.NEW_BARREL_EVENT:
                        self.throwing = True
                        self.throw_frame = 0
                        new_barrel = Barrel(BARREL_X, BARREL_Y, self.platforms, self.borders)
                        self.barrels.append(new_barrel)
                        new_interval = random.randint(MIN_BARREL_SPAWN, MAX_BARREL_SPAWN)
                        py.time.set_timer(self.NEW_BARREL_EVENT, new_interval)

                if self.throwing and self.dk_mode == 'idle':
                    self.dk_mode = 'prethrow'
                    self.throwing = False

                for barrel in self.barrels:
                    barrel.update_barrel()

                self.update_thrower()

                for barrel in self.barrels[:]:
                    if (barrel.rect.right < 0 or barrel.rect.left > SCREEN_WIDTH or
                            barrel.rect.top > SCREEN_HEIGHT or barrel.rect.bottom < 0):
                        self.barrels.remove(barrel)

                for i in range(len(players) - 1, -1, -1):
                    player = players[i]
                    self.player = players[i]
                    self.platforms = players[i].platforms


                    collided_coins = pygame.sprite.spritecollide(player, self.coins, True)
                    if collided_coins:
                        ge[i].fitness += 8 * len(collided_coins)

                    collided_scoins = pygame.sprite.spritecollide(player, self.scoins, True)
                    if collided_scoins:
                        ge[i].fitness += 10 * len(collided_scoins)

                    if player.rect.x == last_positions[i]:
                        stuck_counter[i] += 1
                    else:
                        stuck_counter[i] = 0
                        last_positions[i] = player.rect.x

                    if stuck_counter[i] > 60:
                        ge[i].fitness -= 0.05

                    if not player.is_grounded():
                        if player.rect.x != last_positions[i]:
                            ge[i].fitness += 3

                    for barrel in self.barrels:
                        if (barrel.rect.right > player.rect.left and barrel.rect.left < player.rect.right and
                                barrel.rect.top > player.rect.bottom and 0 < (
                                        barrel.rect.top - player.rect.bottom) < 20):
                            ge[i].fitness += 25


                    teleport_area = pygame.Rect(640, 660, 30, 30)

                    if player.rect.colliderect(teleport_area):
                        player.x = 580
                        player.y = 620
                        player.rect.topleft = (player.x, player.y)

                    hit_by_barrel = any(player.rect.colliderect(barrel.rect) for barrel in self.barrels)
                    if hit_by_barrel:
                        ge[i].fitness -= 20
                        del players[i]
                        del nets[i]
                        del ge[i]
                        del last_positions[i]
                        del stuck_counter[i]
                        del barrel
                        continue

                    if player.rect.y < 0 or player.rect.y > BORDER_HEIGHT:
                        ge[i].fitness -= 100
                        del players[i]
                        del nets[i]
                        del ge[i]
                        del last_positions[i]
                        del stuck_counter[i]
                        continue

                    for br in self.borders:
                        expanded = br.rect.inflate(4, 4)
                        if player.rect.colliderect(expanded):
                            ge[i].fitness -= 5

                    if player.rect.y < player.best_y:
                        pixel_gain = player.best_y - player.rect.y
                        HEIGHT_BONUS_MULTIPLIER = 3  # adjust this to scale bonus
                        bonus = pixel_gain * HEIGHT_BONUS_MULTIPLIER
                        ge[i].fitness += bonus
                        player.best_y = player.rect.y

                    if player.rect.y > player.best_y:
                        ge[i].fitness -= 0.001

                    inputs = player.get_network_inputs(self.ladders, self.barrels, self.princess.rect.y)
                    output = nets[i].activate(inputs)

                    prev_y, prev_x = player.y, player.x

                    current_time = time.time()

                    if output[0] > 0.5 and player.is_grounded():
                        if current_time - self.last_jump_time >= self.jump_cooldown:
                            player.upup()
                            self.last_jump_time = current_time
                            player.jumping = True
                            player.y_at_jump = player.rect.y
                        if not player.is_grounded():
                            if player.jumping and player.best_y == player.y_at_jump:
                                if output[1] > 0.2:
                                    player.move_right()
                                elif output[1] < -0.2:
                                    player.move_left()
                        else:
                            player.jumping = False
                    if output[1] > 0.2:
                        player.move_right()
                    elif output[1] < -0.2:
                        player.move_left()
                    if output[2] > 0.2 and player.on_ladder():
                        player.move_up()
                    elif output[2] < -0.2 and player.on_ladder():
                        player.move_down()

                    player.vel_y += player.gravity
                    player.y += player.vel_y
                    player.rect.y = player.y

                    player.check_collision_platform(self.platforms, prev_y, prev_x)
                    player.check_collision_border(self.borders, prev_x)
                    player.update_animation()


                    if player.rect.colliderect(self.princess.rect):
                        print(f"Igrač {i} je dosegao princezu! Kraj evaluacije.")
                        ge[i].fitness += 1000
                        self.save_winner(ge[i])


                if players and ge:
                    best_genome = max(ge, key=lambda g: g.fitness)
                    self.neat_visualizer.update_visual(config, best_genome)
                    neat_viz_surface = self.neat_visualizer.image

                best_in_gen = max((g.fitness for g in ge), default=float("-inf"))

                if best_in_gen > self.best_ever_fitness:
                    self.best_ever_fitness = best_in_gen

                overlay_data = {
                    "generation": gen - 1,
                    "alive": len(players),
                    "max_fitness": 0 if best_in_gen == float("-inf") else best_in_gen,
                    "max_lifetime": 0 if self.best_ever_fitness == float("-inf") else self.best_ever_fitness,
                }
                self.draw_eval(players, neat_img=neat_viz_surface, overlay_data=overlay_data)

                self.clock.tick(FPS)
                frame += 1

            players.clear()
            nets.clear()
            ge.clear()

        winner = p.run(eval_genomes, generations)
        print('\nBest genome:\n{!s}'.format(winner))

    def _safe_get_events(self):
        try:
            if not py.get_init():
                return []
            if not py.display.get_init():
                return []
            if py.display.get_surface() is None:
                return []
            return py.event.get()
        except Exception:
            return []


    def run(self):
        while not self.game_over:
            for event in self._safe_get_events():
                if event.type == py.QUIT:
                    py.quit()
                    exit()
                elif event.type == self.NEW_BARREL_EVENT:

                    self.throwing = True
                    self.throw_frame = 0

                    new_barrel = Barrel(BARREL_X, BARREL_Y, self.platforms, self.borders)
                    self.barrels.append(new_barrel)

                    new_interval = random.randint(MIN_BARREL_SPAWN, MAX_BARREL_SPAWN)
                    py.time.set_timer(self.NEW_BARREL_EVENT, new_interval)

            if self.throwing:
                if self.dk_mode == 'idle':
                    self.dk_mode = 'prethrow'
                self.throwing = False

            self.update()
            self.draw()
            self.clock.tick(FPS)

        print("Game over. Press R to restart.")
        while True:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    exit()
                elif event.type == py.KEYDOWN:
                    if event.key == py.K_r:
                        print("Game restart...")
                        self.__init__(self.screen)
                        self.run()
                        return
                    elif event.key == py.K_ESCAPE:
                        py.quit()
                        exit()

    def save_winner(self, genome):
        with open("winner.pkl", "wb") as f:
            pickle.dump(genome, f)
        print("Pobjednik je spremljen u 'winner.pkl'!")

    def load_winner(self):
        try:
            with open("winner.pkl", "rb") as f:
                genome = pickle.load(f)
            print("Učitan pobjednički genome!")
            return genome
        except FileNotFoundError:
            print("Nema spremljenog pobjednika!")
            return None

    def run_winner(self, config_path):
        genome = self.load_winner()
        if genome is None:
            print("Nema spremljenog pobjednika! Pokretanje nije moguće.")
            return

        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path)

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        player = Player(PLAYER_X, PLAYER_Y, self.platforms, self.borders, self.ladders)

        frame = 0
        while True:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    exit()

            inputs = player.get_network_inputs(self.ladders, self.barrels)
            output = net.activate(inputs)

            if output[0] > 0.8:
                player.upup()
            if output[1] > 0.5:
                player.move_right()
            elif output[1] < 0.5:
                player.move_left()


            self.screen.fill((0, 0, 0))
            self.screen.blit(self.level_image, (0, 0))
            for platform in self.platforms:
                self.screen.blit(platform.image, platform.rect)
            player.draw(self.screen)
            py.display.flip()

            self.clock.tick(FPS)
            frame += 1

