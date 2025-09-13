from projekt.config import *
py.font.init()

class Node:
    def __init__(self, id, x, y, type, color, label="", index=0):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.color = color
        self.label = label
        self.index = index

    def draw_node(self, surface):
        colors = self.get_node_colors()
        py.draw.circle(surface, colors[0], (self.x, self.y), NODE_RADIUS)
        py.draw.circle(surface, colors[1], (self.x, self.y), NODE_RADIUS - 2)

        text = NODE_FONT.render(self.label, True, WHITE)

        if self.type == INPUT:
            surface.blit(text, (self.x - NODE_RADIUS - text.get_width() - 5, self.y - text.get_height() // 2))
        elif self.type == OUTPUT:
            surface.blit(text, (self.x + NODE_RADIUS + 5, self.y - text.get_height() // 2))

    def get_node_colors(self):
        return [self.color[0], self.color[1]]

class Connection:
    def __init__(self, input_node, output_node, weight):
        self.input = input_node
        self.output = output_node
        self.weight = weight

    def draw_connection(self, surface):
        if self.weight >= 0:
            color = GREEN
            width = max(1, int(abs(self.weight * CONNECTION_WIDTH)))
            start = (self.input.x + NODE_RADIUS, self.input.y)
            end = (self.output.x - NODE_RADIUS, self.output.y)
            py.draw.line(surface, color, start, end, width)
        else:
            # Ako je težina negativna, linija se ne crta
            pass


class NN:
    def __init__(self, config, genome, pos):
        self.nodes = []
        self.connections = []
        self.genome = genome
        self.pos = (int(pos[0] + NODE_RADIUS), int(pos[1]))

        input_names = ["player x", "player y", "is grounded", "is on ladder", "is climbing", "ladder x", "barrel x", "barrel y", "barrel vel x", "barrel vel y", "distance to princess y"]
        output_names = ["Jump", "Right/Left", "Climb ladder"]
        all_nodes = list(genome.nodes.keys())
        nodeIdList = []

        NODE_OFFSET_X = 200
        NODE_OFFSET_Y = 300
        #ulazni cvorovi
        h_in = (INPUT_NEURONS - 1) * (NODE_RADIUS * 2 + NODE_SPACING)
        for i, key in enumerate(config.genome_config.input_keys):
            label = input_names[i] if i < len(input_names) else str(key)
            n = Node(key,
                     pos[0] + NODE_OFFSET_X,
                     pos[1] + NODE_OFFSET_Y + int(-h_in / 2 + i * (NODE_RADIUS * 2 + NODE_SPACING)),
                     INPUT, [GREEN_PALE, GREEN, DARK_GREEN_PALE, DARK_GREEN],
                     label, i)
            self.nodes.append(n)
            nodeIdList.append(key)

        #izlazni cvorovi
        h_out = (OUTPUT_NEURONS - 1) * (NODE_RADIUS * 2 + NODE_SPACING)
        for i, key in enumerate(config.genome_config.output_keys):
            label = output_names[i] if i < len(output_names) else str(key)
            n = Node(key + INPUT_NEURONS,
                     pos[0] + NODE_OFFSET_X + 2 * (LAYER_SPACING + 2 * NODE_RADIUS),
                     pos[1] + NODE_OFFSET_Y + int(-h_out / 2 + i * (NODE_RADIUS * 2 + NODE_SPACING)),
                     OUTPUT, [RED_PALE, RED, DARK_RED_PALE, DARK_RED],
                     label, i)
            self.nodes.append(n)
            nodeIdList.append(key)

        #skriveni cvorovi
        middle_nodes = [n for n in all_nodes if n not in nodeIdList]
        if middle_nodes:
            h_mid = (len(middle_nodes) - 1) * (NODE_RADIUS * 2 + NODE_SPACING)
            for i, key in enumerate(middle_nodes):
                n = Node(key,
                         pos[0] + NODE_OFFSET_X + (LAYER_SPACING + 2 * NODE_RADIUS),
                         pos[1] + NODE_OFFSET_Y + int(-h_mid / 2 + i * (NODE_RADIUS * 2 + NODE_SPACING)),
                         MIDDLE, [BLUE_PALE, DARK_BLUE, BLUE_PALE, DARK_BLUE])
                self.nodes.append(n)
                nodeIdList.append(key)

        for c in genome.connections.values():
            if c.enabled:
                in_key, out_key = c.key
                input_node = self.nodes[nodeIdList.index(in_key)]
                output_node = self.nodes[nodeIdList.index(out_key)]
                self.connections.append(Connection(input_node, output_node, c.weight))

    def draw(self, surface):
        for connection in self.connections:
            connection.draw_connection(surface)
        for node in self.nodes:
            node.draw_node(surface)

class VisualizeNN:
    def __init__(self, pos, size, update_interval=30):
        self.pos = pos
        self.size = size
        self.update_interval = update_interval
        self.frame_counter = 0
        self.image = None

    def update_visual(self, config, genome):
        if self.frame_counter % self.update_interval == 0:
            surface = py.Surface(self.size)
            surface.fill((30, 30, 30))
            nn = NN(config, genome, (0, 0))
            nn.draw(surface)
            self.image = surface
        self.frame_counter += 1

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.pos)
