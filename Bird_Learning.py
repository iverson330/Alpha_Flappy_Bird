#coding=utf-8
# 这是修改过的版本 接口完善过的
import threading
from Tkinter import*
import numpy as np
from time import sleep
import random
# ------------------------------------------------------------------------
class Player:
    def __init__(self, c):
        # 这里的pX, pY都是player的中心点 不是能直接返回的量      中心点在屏幕的中央
        # 是个正方形 边长为10
        self.c = c
        self.pX = 150  # 这个是固定的
        self.pY = 150
        self.v = 0
        self.vnew = 0
        self.p = c.create_rectangle(self.pX-5, self.pY-5, self.pX+5, self.pY+5, fill='red')
        # 左上角x  左上角y   右下角x  右下角y

    def click_move(self):
        self.vnew = 1000
        self.v = 1000
        self.velocity()
    def clean(self):
        self.c.delete(self.p)

    def velocity(self):
        a = 6000
        v = self.v
        self.v = self.vnew
        self.vnew = v - a * 0.01
        dY = (self.vnew*self.vnew-(self.v-a*0.01)*(self.v-a*0.01))/(2*a)
        self.pY = self.pY - dY
        self.c.move(self.p, 0, -dY)

    def get_player_information(self):
        # 反馈player右下角的坐标
        X_player_right_down = self.pX + 5
        Y_player_right_down = self.pY + 5
        return X_player_right_down, Y_player_right_down

class Obstacle:
    # 障碍生成函数
    # 随机数生成3个  注意不能有间断
    def __init__(self, c):
        self.R1 = []  # 放上面矩形的
        self.R2 = []    # 放下面矩形的
        self.R_coordinate = []  #洞的坐标 里面是中心位置的坐标
        self.c = c

    def setalot(self):
        # 现在要设置的是一个“洞” 上下共长120  宽10
        #
        self.mX = 260  # 设置第一个障碍物的中心横坐标
        self.mY = random.randint(60,240)
        self.aX = self.mX - 5   #  计算四个角的高度
        self.aY = self.mY - 60
        self.bX = self.mX + 5
        self.bY = self.mY + 60
        # print self.aX, self.aY, self.bX, self.bY
        # 找一个list储存 障碍物空洞中心的坐标
        self.R_coordinate.append([self.mX, self.mY])   ##############################################
        r1 = self.c.create_rectangle(self.aX, 0, self.bX, self.aY, fill='black')
        r2 = self.c.create_rectangle(self.aX, self.bY, self.bX, 300 ,fill='black')
        self.R1.append(r1)
        self.R2.append(r2)

    def ob_move(self):
        d = 1
        for i in range(len(self.R1)):
            self.c.move(self.R1[i], -d, 0)
            self.c.move(self.R2[i], -d, 0)
            self.R_coordinate[i][0] = self.R_coordinate[i][0] - d

    def clean(self):
        for i in range(len(self.R_coordinate)):
            self.c.delete(self.R1[i])
            self.c.delete(self.R2[i])

    def roll(self):
        # 如果障碍移动出了屏幕 那么就删除它的所有信息
        if self.R_coordinate[0][0] < -5:
            del self.R1[0]
            del self.R2[0]
            del self.R_coordinate[0]

class Game:
    def __init__(self):
        self.root = Tk()
        self.c = Canvas(self.root, width=300, height=300, bg='white')
        self.c.pack()

        self.reward = [-1000, 1]
        self.generate_state_list()
        print self.__state_list

        self.__state = []
        self.__next_state = []
        self.Q = np.zeros([671, 2], dtype=int)

        self.click_flag = False

        self.state = 1

    def button_Click(self):
        self.click_flag = True

    def collision(self):
        # player   self.pX=50  pY
        # ob   self.R_coordinate

        # 检测碰撞与出界
        # 要return state
        pY = self.game_player.pY
        R_coordinate_list = self.game_obstacle.R_coordinate
        face_ob_coordinate_list = []
        # 要检测player面对的是哪个障碍物
        for ob in range(len(R_coordinate_list)):
            if (R_coordinate_list[ob][0]+5) > (150-5):
                face_ob_coordinate_list.append(R_coordinate_list[ob])
        face_ob_coordinate = face_ob_coordinate_list[0]
        face_ob_mX = face_ob_coordinate[0]
        face_ob_mY = face_ob_coordinate[1]
        face_ob_Left_X = face_ob_mX - 5
        face_ob_Right_X = face_ob_mX + 5  #
        face_ob_Up_Y = face_ob_mY - 60
        face_ob_Down_Y = face_ob_mY + 60  #
        self.face_ob_info = [face_ob_Right_X, face_ob_Down_Y]

        if pY < 5 or pY > 295:
            self.state = 0
            print 'fail 1 '

        elif ((150+5) > face_ob_Left_X and face_ob_Right_X > (150-5)) and not ((pY-5 > face_ob_Up_Y) and (pY+5 < face_ob_Down_Y)):
            # 条件里面 左边的大括号是x触碰
            self.state = 0
            print 'fail 2'
        # player 和障碍物碰到
        # 与上面碰到 或者 与下面碰到

    def get_player_information(self):
        (X_player_right_down, Y_player_right_down) = self.game_player.get_player_information()
        (face_ob_Right_X, face_ob_Down_Y) = self.face_ob_info
        dx = face_ob_Right_X - X_player_right_down
        dy = face_ob_Down_Y - Y_player_right_down
        return dx, dy, self.state

    # ----------------------------------------------------------------------------
    def discretize_state(self,state):
        dx = state[0]
        dy = state[1]
        live_state = state[2]
        if dx == 110:
            dx = dx - 1
        dx = int(dx/10)
        dy = int(dy/10)
        m = dx * 61 + (dy+30)
        return m, live_state

    def generate_state_list(self):
        self.__state_list = []
        for x in range(0, 11):
            for y in range(-30, 31):
                self.__state_list.append((x, y))

    def learn(self):
        # 这里还有一个问题
        # 必须要隔一秒获取信息才是有效的
        # 如果
        self.__state = self.get_player_information()
        self.m, state = self.discretize_state(self.__state)
        if self.Q[self.m][0] < self.Q[self.m][1]: # 要替换为要采取的action条件
            self.button_Click()
            self.a = 1
        else:
            self.a = 0

    # ----------------------------------------------------------------------------
    def run(self):
        self.game_player = Player(self.c)
        self.game_obstacle = Obstacle(self.c)
        self.game_obstacle.setalot()
        self.player_coordinates = self.game_player.get_player_information()  # 这个到后面要改的  返回得到的只是中心点的数据
        self.c.update()

        self.face_ob_info = []
        m = 0
        u = 110                 #   random.randint(100, 120)  #  这里就是控制出现障碍的时间
        while self.state == 1:
            # self.tLock.acquire()
            for num in range(2):
                m = m + 1
                self.game_obstacle.ob_move()
                self.collision()
                if self.click_flag == True:
                    self.game_player.click_move()
                elif self.click_flag == False:
                    self.game_player.velocity()
                self.game_obstacle.roll()
                # if m % 2 == 0:
                    # print self.get_player_information()
                if m >= u:
                    m = 0
                    self.game_obstacle.setalot()
                self.c.update()
                sleep(0.01)
                self.click_flag = False

            if self.__state == []:
                pass
            else:
                self.__next_state = self.get_player_information()
                print self.__next_state
                new_m, state = self.discretize_state(self.__next_state)
                print new_m, self.__state_list[new_m], state
                if state == 1:
                    d_reward = 1
                else:
                    d_reward = -1000
                self.Q[self.m][self.a] = self.Q[self.m][self.a] + d_reward
            self.learn()
# ------------------------------------------------------------------------
Bird = Game()
Bird.run()
while Bird.state == 0:
    Bird.game_obstacle.clean()
    Bird.game_player.clean()
    Bird.c.update()
    Bird.state = 1
    Bird.run()










