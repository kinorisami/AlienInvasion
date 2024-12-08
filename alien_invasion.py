import sys
import pygame
from time import sleep

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.settings = Settings()
        # self.screen =pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_width()
        # self.settings.screen_height = self.screen.get_height()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption('Alien Invasion')
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()
        self.game_active = False
        self.play_button = Button(self, 'Play')


    def run_game(self):
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()      # 在对编组进行update时编组会自动对其中的每个精灵调用update（）
                self._update_bullets()
                # print(len(self.bullets))
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60)
            # pygame将保证这个循环每秒恰好运行60次


    # 辅助方法一般只在类中调用，不会在类外调用
    def _check_events(self):

        for event in pygame.event.get():
            # pygame.event.get()函数返回一个列表，其中包含它在上一次调用后发生的所有事件
            if event.type == pygame.QUIT:
                self.stats.save_high_score()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos):

        button_clicked =self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active :
            # rect.collidepoint()方法检查鼠标的单机位置是否在play按钮的rect内
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            self.bullets.empty()
            self.aliens.empty()

            self._create_fleet()
            self.ship.center_ship()

            # 隐藏光标
            pygame.mouse.set_visible(False)


    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self.stats.save_high_score()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()


    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False


    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _create_fleet(self):

        alien = Alien(self)
        alien_width,alien_height = alien.rect.size #该属性是一个元组包含宽度和高度


        current_x,current_y = alien_width,alien_height
        while current_y<(self.settings.screen_height -3 * alien_height):
            while current_x <= self.settings.screen_width -2 * alien_width:
                self._create_alien(current_x,current_y)
                current_x += 2*alien_width

            current_x =alien_width
            current_y += alien_height*2

    def _create_alien(self, x_position ,y_position):
        new_alien = Alien(self)
        new_alien.x = x_position

        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.bullets.empty()
            self.aliens.empty()

            self._create_fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.y >= self.settings.screen_height:
                self._ship_hit()
                break

    def _update_bullets(self):
        # 更新子弹位置
        self.bullets.update()
        # 删除消失的子弹
        for bullet in self.bullets.copy():
            # python要求遍历过程中列表保持不变，所以使用列表副本进行遍历
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()


    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(self.aliens, self.bullets, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()
        if not self.aliens:
            self.bullets.empty()  # empty（）方法删除编组下所有精灵
            self._create_fleet()
            self.settings.increase_speed()

            self.stats.level += 1
            self.sb.prep_level()


    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            # spritecollideany()函数接受两个实参，它检查编组是否有成员与精灵发生了碰撞，并在找到与精灵发成碰撞的成员后停止遍历编组
            #如果没有发生碰撞则返回None
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break





    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        # fill()方法只能接受一个颜色的实参
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()
        # 它在每次执行while循环时都绘制一个空屏幕，并擦去旧屏幕



if __name__ == '__main__':
    # 仅当直接运行该文件时它才会执行
    ai = AlienInvasion()
    ai.run_game()
