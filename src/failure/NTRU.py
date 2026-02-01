from mpmath import mp
from .util import *

def log2(x):
    if x == 0:
        return 0
    return mp.log(x, 2)

def calculate_decryption_failure_probability(n, q):
    wt = q // 8 - 2

    # 定义 f 的分布
    t = {0: 1/3, 1: 2/3}
    Df = iter_law_convolution(t, n - 1)
    Df = dist_scale(Df, 9)

    # 定义 g 的分布
    Dg = {9 * wt: 1}

    # 计算 one-shot 分布
    t_fm = {-1: 1/3, 0: 1/3, 1: 1/3}
    Dfm = iter_law_convolution(t_fm, wt)
    Dfm = dist_scale(Dfm, 3)

    t_gr = {-3: 1/2, 3: 1/2}
    Dgr = iter_law_convolution(t_gr, wt)
    one_shot_dist = law_convolution(Dfm, Dgr)

    # 计算阈值
    threshold = q // 2 - 2

    # 计算解密失败概率
    failure_probability = tail_probability(one_shot_dist, threshold)
    return failure_probability

def compute_failure_probability(**params):
    '''
    计算解密失败概率，并返回一个格式化的字符串
    '''
    n = int(params.get("n"))
    q = int(params.get("q"))
    mp.dps = 50  # 设置高精度
    failure_prob = calculate_decryption_failure_probability(n, q)
    # 计算对数：失败概率的对数形式
    failure_prob_log2 = -mp.log(failure_prob, 2)
    failure_prob_log2_float = float(failure_prob_log2)
    return f"Parameters: n={n}, q={q}\nDecryption failure probability: 2^(-{failure_prob_log2_float:.2f})"
