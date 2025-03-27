import pygame

class Leaderboard:
    """Stocke, met à jour et affiche le tableau des scores."""

    def __init__(self, font, font_color, max_items, width, data=None):
        self.font = font
        self.font_color = font_color
        self.max_items = max_items

        self.section_width = width
        self.text_height = font.get_height()
        self.horizontal_margin = 2 * font.size("|")[0]
        self.vertical_margin = 0.5 * self.text_height

        self.width = self.section_width
        self.height = ((2 + max_items) * self.vertical_margin
                       + (1 + max_items) * self.text_height)

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.surface.get_rect()

        self.title = font.render("TOP 3 WINNERS", True, font_color)
        self.list_start_y = (self.vertical_margin + self.text_height
                             + self.vertical_margin)

        if data is None:
            self.data = {'EASY': [], 'NORMAL': [], 'HARD': []}
        else:
            self.data = data

        self._prepare_render()

    def _prepare_surface(self):
        """Prépare la surface avec tous les titres."""
        self.surface.fill((0, 0, 0, 0))

        title_top = self.vertical_margin
        frame_x = 0
        frame_y = title_top + self.text_height + self.vertical_margin
        pygame.draw.line(self.surface, self.font_color,
                         (frame_x, frame_y),
                         (self.width, frame_y))
        pygame.draw.line(self.surface, self.font_color,
                         (frame_x, frame_y),
                         (frame_x, self.height))
        pygame.draw.line(self.surface, self.font_color,
                         (self.width - 1, frame_y),
                         (self.width - 1, self.height))
        pygame.draw.line(self.surface, self.font_color,
                         (frame_x, self.height - 1),
                         (self.width, self.height - 1))

        title_rect = self.title.get_rect(
            top=self.vertical_margin, centerx=0.5 * self.width)
        self.surface.blit(self.title, title_rect)

    def _prepare_render(self):
        """Prépare la surface à rendre."""
        self._prepare_surface()
        x_name = self.horizontal_margin
        x_time = self.section_width - self.horizontal_margin

        # Combine tous les scores et les trie
        all_scores = []
        for difficulty in ["EASY", "NORMAL", "HARD"]:
            all_scores.extend(self.data[difficulty])
        all_scores.sort(key=lambda x: x[1])  # Trie par temps

        # Affiche uniquement les 3 meilleurs scores
        y = self.list_start_y
        for name, time in all_scores[:3]:
            name_image = self.font.render(name, True, self.font_color)
            score_image = self.font.render(str(time), True, self.font_color)
            time_width = self.font.size(str(time))[0]
            self.surface.blit(name_image, (x_name, y))
            self.surface.blit(score_image, (x_time - time_width, y))
            y += self.text_height + self.vertical_margin

    def needs_update(self, difficulty, time):
        """Vérifie si le tableau des scores doit être mis à jour."""
        if difficulty not in self.data:
            return False

        data = self.data[difficulty]
        if len(data) < self.max_items:
            return True

        return data[-1][1] > time

    def update(self, difficulty, name, time):
        """Met à jour le tableau des scores."""
        if difficulty not in self.data:
            return

        data = self.data[difficulty]
        i = 0
        while i < len(data) and time >= data[i][1]:
            i += 1
        data.insert(i, (name, time))

        if len(data) > self.max_items:
            data.pop()

        self._prepare_render()  # Assurez-vous que la surface est ré-rendue

    def draw(self, surface):
        """Dessine sur la surface."""
        surface.blit(self.surface, self.rect)
