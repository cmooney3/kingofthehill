import random
import math
import ImageDraw
from PIL import Image


class Gaussian2D:
    """ http://en.wikipedia.org/wiki/Gaussian_function """
    def __init__(self, center, sigma, theta):
        self.cx, self.cy = center
        sx, sy = sigma
        self.a = (math.cos(theta)**2) / (2 * sx**2) +
                 (math.sin(theta)**2) / (2 * sy**2)
        self.b = (math.sin(2*theta)) / (4 * sy**2) -
                 (math.sin(2*theta)) / (4 * sx**2)
        self.c = (math.sin(theta)**2) / (2 * sx**2) +
                 (math.cos(theta)**2) / (2 * sy**2)

    def value(self, point):
        x, y = point
        return math.exp(-1 * ((self.a * (x - self.cx)**2) +
                              (2 * self.b * (x - self.cx) * (y - self.cy)) +
                              (self.c * (y - self.cy)**2)))


class Map:
    """ A class that represents the relevant features of a game board """

    def __init__(self, width=100, height=80, num_hills=4, hill_size=30):
        self.width, self.height = width, height
        self.payout_rates = self.__generate_payouts(num_hills, hill_size)
        self.p1_spawn, self.p2_spawn = self.__generate_spawn_points()

    def __mirror(self, x, y):
        """ Mirror a point over the diagonal of the map """
        return (self.width - x - 1, self.height - y - 1)

    def __generate_payouts(self, num_hills, hill_size):
        """ Compute several gaussians and build the payout map """
        hills = []
        for i in range(num_hills):
            cx = random.randint(0, self.width - 1)
            cy = random.randint(0, self.height - 1)
            sx = random.random() * hill_size + 1
            sy = random.random() * hill_size + 1
            theta = random.random() * math.pi
            hills.append(Gaussian2D((cx, cy), (sx, sy), theta))
            # Add a mirror image one too to make the map fair
            hills.append(Gaussian2D(self.__mirror(cx, cy), (sx, sy), theta + math.pi))

        payout_rates = [[0.0] * self.height for x in range(self.width)]
        for y in range(self.height):
            for x in range(self.width):
                payout_rates[x][y] = sum([h.value((x,y)) for h in hills])

        return payout_rates

    def __generate_spawn_points(self):
        """ Keep trying random points until it's mirror is far enough away """
        while True:
            p1x = random.randint(0, self.width - 1)
            p1y = random.randint(0, self.height - 1)
            p2x, p2y = self.__mirror(p1x, p1y)
            d_sq = (p1x - p2x)**2 + (p1y - p2y)**2
            if d_sq >= (self.width / 2)**2:
                break
        return (p1x, p1y), (p2x, p2y)

    def to_image(self, filename):
        S = 20  # Cell (S)ize.  I got sick of typing a long constant name
        img = Image.new('RGB', (self.width * S, self.height * S), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        black = (0, 0, 0)

        # First fill in the heatmap
        max_val = max([max(row) for row in self.payout_rates])
        for y in range(self.height):
            for x in range(self.width):
                shade = int(float(self.payout_rates[x][y]) / max_val * 255)
                fill_color = (shade, shade, shade)
                draw.polygon([(x*S, y*S), (x*S+S,y*S), (x*S+S, y*S+S), (x*S,y*S+S)],
                             fill=fill_color, outline=black)

        # Mark the spawn points
        x, y = self.p1_spawn
        draw.ellipse((x*S, y*S, x*S+S, y*S+S), fill=(255, 0, 0), outline=black)
        x, y = self.p2_spawn
        draw.ellipse((x*S, y*S, x*S+S, y*S+S), fill=(0, 0, 255), outline=black)

        img.save(filename)


if __name__ == '__main__':
    m = Map()
    m.to_image('out.png')
