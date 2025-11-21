"""
O(T*K)
デフォルトではK=500 time=6500 epsilon=0.1 thetaは正規分布(0.5,0.1)でサンプリング
"""

"""
    腕(arm)K本の多腕バンディット問題をε-greedy法で解くプログラム
    各腕の報酬確率thetaは0~1の正規分布に従う範囲の値をとるとする。
    MultiBandit(epsilon,theta,time=1000)
"""

import math
import random
from scipy.stats import truncnorm

def main():
    epsilon = 0.1  
    numberOfArms = 10
    theta = sample_truncated_normal_on_01(n_samples=numberOfArms, mu=0.5, sigma=0.2)
    for i, th in enumerate(theta):
        print(f"arm {i}: theta={th:.4f}")
    AR,arms = MultiBandit(epsilon,theta)
    print("accumulated reword",AR)
    

def initArm(theta) -> list:
    arms = []
    for th in theta:
        arm = {
            "theta": th,
            "numOfTimes": 0,
            "rewords": 0,
        }
        arms.append(arm)
    return arms

def Reword(arm: dict) -> int:
    #選ばれた腕 a_i の確率 theta に基づいて報酬を返す（0 or 1）。
    if random.random() < float(arm.get("theta", 0.0)):
        return 1
    return 0

"""切断正規から n_samples 個の乱数を生成して返す"""
def sample_truncated_normal_on_01(n_samples=1000, mu=0.5, sigma=0.1, random_state=None):
    lower, upper = 0.0, 1.0
    # 標準化
    a, b = (lower - mu) / sigma, (upper - mu) / sigma
    # 切断正規分布からサンプルを生成
    samples = truncnorm.rvs(a, b, loc=mu, scale=sigma, size=n_samples, random_state=random_state)
    return samples 

""" 総報酬とarmsを返すマルチバンディット関数 """
def MultiBandit(epsilon,theta,time=6500):
    arms = initArm(theta)
    for t in range(time):
        # epsilonの行動選択
        if random.random() < epsilon:
            choice = random.randrange(len(arms))
        else:
            # 現在の平均報酬が最大の腕を選ぶ
            def avg(arm):
                n = arm.get("numOfTimes", 0)
                if n == 0:
                    return 0
                else:
                    return (arm.get("rewords", 0) / n)
            # 平均報酬の計算と最大値の探索
            # max_valと近い値をもつ腕を候補にしてランダムに選ぶ
            # iscloseは浮動小数点の比較に使用（誤差10^-9を許容）
            vals = [avg(a) for a in arms]
            max_val = max(vals)
            candidates = [i for i, v in enumerate(vals) if math.isclose(v, max_val)]
            choice = random.choice(candidates)

        r = Reword(arms[choice])
        arms[choice]["numOfTimes"] += 1
        arms[choice]["rewords"] += r
    
    return sum(a["rewords"] for a in arms),arms
    
if __name__ == "__main__":
    main()

