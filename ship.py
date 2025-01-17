import pygame

from pygame.sprite import Sprite



class Ship(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings
        # 得到屏幕的矩形特征

        self.moving_right = False
        self.moving_left = False
        self.image =pygame.image.load('images/ship.bmp') # 返回一个表示飞船的surface
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)



    def update(self):
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        self.rect.x =self.x


    def center_ship(self):
        self.rect.midbottom =self.screen_rect.midbottom
        self.x = float(self.rect.x)


    def blitme(self):
        """将图像绘制到self.rect的指定位置"""
        self.screen.blit(self.image, self.rect)

