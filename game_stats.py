import os

class GameStats:
    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.reset_stats()

        # 读取最高分
        self.high_score = self.read_high_score()

    def reset_stats(self):
        self.score = 0
        self.level = 1
        self.ships_left = self.settings.ship_limit

    def read_high_score(self):
        if os.path.exists("data/high_score.txt"):
            with open("data/high_score.txt", "r") as file:
                content = file.read().strip()  # 去除多余的空白字符
                if content.isdigit():  # 确保内容是一个有效的数字
                    return int(content)
                else:
                    return 0  # 如果内容不是数字，返回0
        return 0  # 如果文件不存在，返回0


    def save_high_score(self):
        # 保存最高分到文件
        with open("data/high_score.txt", "w") as file:
            file.write(str(self.high_score))
