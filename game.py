import pygame 
import math 
import random 
import os
 
# 初始化 
pygame.init() 
WIDTH, HEIGHT = 800, 600 
screen = pygame.display.set_mode((WIDTH,  HEIGHT))
pygame.display.set_caption("Space  mining")  # 设置窗口标题 
clock = pygame.time.Clock() 
 
# 颜色常量 
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 191, 255)
RED = (255, 0, 0)
 
# 加载声音 
# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建 WAV 文件的相对路径
sound_file_path1 = os.path.join(script_dir, 'sounds', 'shoot.wav')
sound_file_path2 = os.path.join(script_dir, 'sounds', 'hit.wav')
sound_file_path3 = os.path.join(script_dir, 'sounds', 'explosion.wav')

pygame.mixer.init() 
shoot_sound = pygame.mixer.Sound(sound_file_path1) 
hit_sound = pygame.mixer.Sound(sound_file_path2) 
explosion_sound = pygame.mixer.Sound(sound_file_path3) 
 
# 玩家飞船类 
class Spaceship:
    def __init__(self):
        self.x = WIDTH//2 
        self.y = HEIGHT//2 
        self.angle  = 0 
        self.speed  = 0 
        self.acceleration  = 0.2 
        self.max_speed  = 5 
        self.lives  = 3 
        self.score  = 0 
        self.size  = 30  # 飞船初始大小 
        self.bullets  = []
        self.exploding  = False 
        self.explosion_frames  = 0 
        self.shoot_cooldown  = 0  # 子弹发射冷却时间 
    
    def update(self):
        if self.exploding: 
            self.explosion_frames  += 1 
            if self.explosion_frames  > 30:
                self.exploding  = False 
                self.explosion_frames  = 0 
            return 
        
        keys = pygame.key.get_pressed() 
        # 方向控制 
        if keys[pygame.K_LEFT]:
            self.angle  += 5 
        if keys[pygame.K_RIGHT]:
            self.angle  -= 5 
        # 推进控制 
        if keys[pygame.K_UP]:
            self.speed  = min(self.speed  + self.acceleration,  self.max_speed) 
        else:
            self.speed  = max(self.speed  - 0.1, 0)
        
        # 计算移动 
        rad = math.radians(self.angle) 
        self.x += self.speed  * math.cos(rad) 
        self.y -= self.speed  * math.sin(rad) 
        
        # 边界检测 
        self.x = self.x % WIDTH 
        self.y = self.y % HEIGHT 
    
    def shoot(self):
        if self.shoot_cooldown  <= 0:
            rad = math.radians(self.angle) 
            bullet = Bullet(self.x, self.y, rad)
            self.bullets.append(bullet) 
            shoot_sound.play() 
            self.shoot_cooldown  = 10  # 设置子弹发射冷却时间 
        else:
            self.shoot_cooldown  -= 1 
    
    def explode(self):
        self.exploding  = True 
        self.lives  -= 1 
        self.size  = max(self.size  - 5, 10)  # 飞船变小，最小为 10 
        explosion_sound.play() 
    
    def draw(self):
        if self.exploding: 
            pygame.draw.circle(screen,  RED, (int(self.x), int(self.y)), 30 - self.explosion_frames,  3)
        else:
            # 绘制三角形飞船 
            points = [
                (self.x + self.size  * math.cos(math.radians(self.angle)),  
                 self.y - self.size  * math.sin(math.radians(self.angle))), 
                (self.x + (self.size  - 10) * math.cos(math.radians(self.angle  + 150)), 
                 self.y - (self.size  - 10) * math.sin(math.radians(self.angle  + 150))),
                (self.x + (self.size  - 10) * math.cos(math.radians(self.angle  - 150)), 
                 self.y - (self.size  - 10) * math.sin(math.radians(self.angle  - 150))),
            ]
            pygame.draw.polygon(screen,  BLUE, points, 3)
 
# 子弹类 
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x 
        self.y = y 
        self.angle  = angle 
        self.speed  = 10 
    
    def update(self):
        self.x += self.speed  * math.cos(self.angle) 
        self.y -= self.speed  * math.sin(self.angle) 
    
    def draw(self):
        pygame.draw.circle(screen,  RED, (int(self.x), int(self.y)), 3)
 
# 矿石类 
class Asteroid:
    def __init__(self):
        self.x = random.randint(0,  WIDTH)
        self.y = random.randint(0,  HEIGHT)
        self.size  = random.randint(30,  60)
        self.angle  = random.uniform(0,  360)
        self.speed  = random.uniform(1,  3)
        self.hits  = 0 
        self.points  = self.generate_points() 
    
    def generate_points(self):
        points = []
        for _ in range(random.randint(5,  10)):
            angle = random.uniform(0,  360)
            radius = self.size  // 2 + random.randint(-5,  5)
            x = self.x + radius * math.cos(math.radians(angle)) 
            y = self.y + radius * math.sin(math.radians(angle)) 
            points.append((x,  y))
        return points 
    
    def update(self):
        rad = math.radians(self.angle) 
        self.x += self.speed  * math.cos(rad) 
        self.y -= self.speed  * math.sin(rad) 
        
        # 边界检测 
        self.x = self.x % WIDTH 
        self.y = self.y % HEIGHT 
        self.points  = self.generate_points() 
    
    def draw(self):
        pygame.draw.polygon(screen,  YELLOW, self.points,  2)
 
# 游戏对象 
player = Spaceship()
asteroids = [Asteroid() for _ in range(5)]
high_score = 0 
 
# 游戏循环 
running = True 
game_over = False 
 
while running:
    screen.fill(BLACK) 
    
    # 事件处理 
    for event in pygame.event.get(): 
        if event.type  == pygame.QUIT:
            running = False 
        if event.type  == pygame.KEYDOWN:
            if event.key  == pygame.K_F1 and game_over:
                player = Spaceship()
                asteroids = [Asteroid() for _ in range(5)]
                game_over = False 
    
    if not game_over:
        # 更新状态 
        player.update() 
        
        # 按住空格键连续发射子弹 
        keys = pygame.key.get_pressed() 
        if keys[pygame.K_SPACE]:
            player.shoot() 
        
        # 更新子弹 
        for bullet in player.bullets[:]: 
            bullet.update() 
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                player.bullets.remove(bullet) 
        
        # 更新矿石 
        for asteroid in asteroids[:]:
            asteroid.update() 
            # 碰撞检测：矿石与飞船 
            distance = math.hypot(player.x  - asteroid.x, player.y - asteroid.y)
            if distance < asteroid.size//2  + player.size//2  and not player.exploding: 
                player.explode() 
            # 碰撞检测：子弹与矿石 
            for bullet in player.bullets[:]: 
                distance = math.hypot(bullet.x  - asteroid.x, bullet.y - asteroid.y)
                if distance < asteroid.size//2  + 3:
                    asteroid.hits  += 1 
                    player.score  += 5  # 每次击中得分 
                    if asteroid.hits  >= 3:
                        asteroids.remove(asteroid) 
                    else:
                        asteroid.size  //= 2 
                    player.bullets.remove(bullet) 
                    hit_sound.play() 
        
        # 生成新矿石 
        if len(asteroids) < 5:
            asteroids.append(Asteroid()) 
        
        # 检查游戏是否结束 
        if player.lives  <= 0:
            game_over = True 
            if player.score  > high_score:
                high_score = player.score  
    
    # 绘制元素 
    for asteroid in asteroids:
        asteroid.draw() 
    player.draw() 
    for bullet in player.bullets: 
        bullet.draw() 
    
    # 显示分数、生命值和最高分 
    font = pygame.font.SysFont('arial',  24)
    score_text = font.render(f'Score:  {player.score}',  True, WHITE)
    lives_text = font.render(f'Lives:  {"A" * player.lives}',  True, WHITE)
    high_score_text = font.render(f'High  Score: {high_score}', True, WHITE)
    screen.blit(score_text,  (10, 10))
    screen.blit(lives_text,  (WIDTH - 150, 10))
    screen.blit(high_score_text,  (WIDTH//2 - 70, 10))
    
    # 显示提示信息 
    if game_over:
        game_over_text = font.render('Game  Over!', True, WHITE)
        restart_text = font.render('Press  F1 to restart.', True, WHITE)
        screen.blit(game_over_text,  (WIDTH//2 - 70, HEIGHT//2 - 20))
        screen.blit(restart_text,  (WIDTH//2 - 100, HEIGHT//2 + 20))
    
    pygame.display.flip() 
    clock.tick(60) 
 
pygame.quit() 
