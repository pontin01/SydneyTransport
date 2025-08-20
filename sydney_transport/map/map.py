import subprocess
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

from sydney_transport.map.exploration_routes import ExplorationRoutes
from sydney_transport.map.optimal_route import OptimalRoute

from sydney_transport.components.stop import Stop

class Map:
    def __init__(self, colour_mode: str, start_stop: Stop, end_stop: Stop):
        # app functionality variables
        self.HEIGHT, self.WIDTH = self._get_app_height_and_width()
        self.SCALE = self.HEIGHT / 4320
        self.screen = None
        self.transparent_layer = None
        self.colour_mode = colour_mode

        self.exploration_routes = None
        self.optimal_route = None

        self.start_stop = start_stop
        self.end_stop = end_stop

    @staticmethod
    def _get_app_height_and_width() -> tuple[int, int]:
        resolution_str = (
            subprocess.Popen(
                "xrandr | grep \\* | cut -d' ' -f4 | head -n 1",
                shell=True,
                stdout=subprocess.PIPE
            )
            .communicate()[0]
            .decode()
            .strip()
        )

        _, screen_height_str = resolution_str.split("x")
        screen_height = int(screen_height_str)

        app_width = int(screen_height / 2) * 3

        return screen_height, app_width

    def run(self):
        self._setup()
        self._main_loop()

    def _setup(self) -> None:
        pygame.init()

        # initialise app functionality variables
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.transparent_layer = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        self.exploration_routes: ExplorationRoutes = ExplorationRoutes(self.SCALE, self.colour_mode,
                                                                       self.start_stop, self.end_stop)
        self.optimal_route: OptimalRoute = OptimalRoute(self.SCALE)

    def _main_loop(self) -> None:
        background_image = self._get_background()

        # main game loop
        running = True
        drawing_exploration_routes = True
        drawing_optimal_route = False
        while running:
            # user pressed X to exit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.exploration_routes.draw_next_line(self.transparent_layer)

            # draw exploration routes
            if drawing_exploration_routes:
                drawing_exploration_routes = self.exploration_routes.draw_next_line(self.transparent_layer)

                # delay drawing of optimal route
                if not drawing_exploration_routes:
                    pygame.time.wait(2000)
                    drawing_optimal_route = True

            # draw optimal route
            if drawing_optimal_route:
                drawing_optimal_route = self.optimal_route.draw_next_line(self.transparent_layer)

            self.screen.blit(background_image, (0, 0))
            self.screen.blit(self.transparent_layer, (0, 0))
            pygame.display.flip()

        pygame.quit()

    def _get_background(self) -> pygame.Surface:
        path = os.getcwd() + "/../docs/map_8k.jpg"
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (self.WIDTH, self.HEIGHT))
