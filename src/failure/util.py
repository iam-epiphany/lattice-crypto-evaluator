from math import factorial as fac, floor
from math import log, ceil, erf, sqrt, exp
import numpy as np

# =============================
# 与高斯分布相关的工具函数
# =============================

def gaussian_center_weight(sigma, t):
    """
    计算连续高斯分布在区间 [-t, t] 内的概率质量
    用于估计离散高斯截断误差

    参数
    ----
    sigma : float
        高斯分布标准差
    t : float
        截断区间上界

    返回
    ----
    float
        erf(t / (sigma * sqrt(2)))
    """
    return erf(t / (sigma * sqrt(2.)))


# =============================
# 中心二项分布（Kyber 使用）
# =============================

def binomial(x, y):
    """
    二项式系数 C(y, x)

    参数
    ----
    x : int
    y : int

    返回
    ----
    int
        C(y, x)，若非法则返回 0
    """
    try:
        binom = fac(x) // fac(y) // fac(x - y)
    except ValueError:
        binom = 0
    return binom


def centered_binomial_pdf(k, x):
    """
    中心二项分布的概率质量函数

    参数
    ----
    k : int
        分布参数
    x : int
        自变量，x ∈ [-k, k]

    返回
    ----
    float
        P(X = x)
    """
    return binomial(2 * k, x + k) / 2. ** (2 * k)


def build_centered_binomial_law(k):
    """
    构造中心二项分布的概率分布表

    参数
    ----
    k : int
        分布参数

    返回
    ----
    dict
        {x : P(X = x)}, x ∈ [-k, k]
    """
    D = {}
    for i in range(-k, k + 1):
        D[i] = centered_binomial_pdf(k, i)
    return D


# =============================
# 新增 1：离散高斯分布
# =============================

def build_discrete_gaussian_law(sigma):
    """
    构造离散高斯分布 D_{Z, sigma} 的概率分布表（截断）
    """
    tail = 3
    B = int(floor(tail * sigma))
    D = {}

    # 未归一化概率
    for x in range(-B, B + 1):
        D[x] = exp(- (x * x) / (2 * sigma * sigma))

    # 归一化
    Z = sum(D.values())
    for x in D:
        D[x] /= Z

    return D


# =============================
# 新增 2：稀疏三元分布
# =============================

def build_sparse_ternary_law(p):
    """
    构造稀疏三元分布

    P(X = -1) = p
    P(X =  0) = 1 - 2p
    P(X =  1) = p

    参数
    ----
    p : float
        非零概率的一半，要求 0 <= p <= 0.5

    返回
    ----
    dict
        {-1: p, 0: 1-2p, 1: p}
    """
    assert 0 <= p <= 0.5
    return {
        -1: p,
         0: 1 - 2 * p,
         1: p
    }


# =============================
# 新增 3：均匀分布
# =============================

def build_uniform_law(B):
    """
    构造区间 [-B, B] 上的离散均匀分布

    参数
    ----
    B : int
        支撑区间上界

    返回
    ----
    dict
        {x : 1/(2B+1)}, x ∈ [-B, B]
    """
    size = 2 * B + 1
    p = 1.0 / size
    return {x: p for x in range(-B, B + 1)}


# =============================
# 模数切换与误差分布
# =============================

def mod_switch(x, q, rq):
    """
    模数切换（Torus 上的重新离散化）

    参数
    ----
    x : int
        输入值
    q : int
        原模数
    rq : int
        目标模数

    返回
    ----
    int
        切换后的值
    """
    return int(round(1.0 * rq * x / q) % rq)


def mod_centered(x, q):
    """
    模 q 的中心化表示（结果落在 (-q/2, q/2]）

    参数
    ----
    x : int
    q : int

    返回
    ----
    int
    """
    a = x % q
    if a < q / 2:
        return a
    return a - q


def build_mod_switching_error_law(q, rq):
    """
    构造模数切换引入的误差分布

    参数
    ----
    q : int
        原模数
    rq : int
        中间模数

    返回
    ----
    dict
        误差分布 {e : P(E = e)}
    """
    D = {}
    for x in range(q):
        y = mod_switch(x, q, rq)
        z = mod_switch(y, rq, q)
        d = mod_centered(x - z, q)
        D[d] = D.get(d, 0) + 1.0 / q
    return D


# =============================
# 分布运算（卷积 / 乘积）
# =============================

def law_convolution(A, B):
    """
    两个独立随机变量之和的分布（卷积）

    参数
    ----
    A : dict
    B : dict

    返回
    ----
    dict
        A + B 的分布
    """
    C = {}
    for a in A:
        for b in B:
            c = a + b
            C[c] = C.get(c, 0) + A[a] * B[b]
    return C


def law_product(A, B):
    """
    两个独立随机变量乘积的分布

    参数
    ----
    A : dict
    B : dict

    返回
    ----
    dict
        A * B 的分布
    """
    C = {}
    for a in A:
        for b in B:
            c = a * b
            C[c] = C.get(c, 0) + A[a] * B[b]
    return C


def clean_dist(A):
    """
    清理概率极小的事件以加速计算
    丢弃概率 < 2^-300 的项

    参数
    ----
    A : dict

    返回
    ----
    dict
    """
    B = {}
    for x, y in A.items():
        if y > 2 ** (-300):
            B[x] = y
    return B


def iter_law_convolution(A, i):
    """
    计算分布 A 的 i 次自卷积（使用二进制快速幂）

    参数
    ----
    A : dict
        输入分布
    i : int
        卷积次数

    返回
    ----
    dict
        i 次卷积后的分布
    """
    D = {0: 1.0}
    i_bin = bin(i)[2:]
    for ch in i_bin:
        D = law_convolution(D, D)
        D = clean_dist(D)
        if ch == '1':
            D = law_convolution(D, A)
            D = clean_dist(D)
    return D


def tail_probability(D, t):
    """
    计算尾概率 P(|X| > t)

    参数
    ----
    D : dict
        离散分布
    t : int
        阈值

    返回
    ----
    float
    """
    if not D:
        return 0.0

    s = 0.0
    ma = max(D.keys())
    if t >= ma:
        return 0.0

    # 从尾部向中心累加，提高数值稳定性
    for i in reversed(range(int(ceil(t)), int(ma))):
        s += D.get(i, 0) + D.get(-i, 0)
    return s



def law_convolution_fft(A, B, eps=1e-18):
    """
    用 FFT 计算两个整数分布 A,B 的卷积
    A,B: dict {int: prob}
    """
    if not A or not B:
        return {}

    amin, amax = min(A), max(A)
    bmin, bmax = min(B), max(B)

    size = (amax - amin) + (bmax - bmin) + 1
    n = 1
    while n < size:
        n <<= 1

    fa = np.zeros(n)
    fb = np.zeros(n)

    for x,p in A.items():
        fa[x - amin] = p
    for x,p in B.items():
        fb[x - bmin] = p

    F = np.fft.fft(fa)
    G = np.fft.fft(fb)
    H = F * G
    h = np.fft.ifft(H).real

    C = {}
    for i in range(size):
        v = h[i]
        if abs(v) > eps:
            C[i + amin + bmin] = v
    return C

def power_law_convolution_fft(A, t, eps=1e-18):
    """
    计算 A 的 t 次自卷积: A^{*t}
    """
    if t == 0:
        return {0:1.0}
    if t == 1:
        return A.copy()

    amin, amax = min(A), max(A)
    width = amax - amin
    size = t * width + 1

    n = 1
    while n < size:
        n <<= 1

    f = np.zeros(n)
    for x,p in A.items():
        f[x - amin] = p

    F = np.fft.fft(f)
    F **= t
    res = np.fft.ifft(F).real

    out = {}
    for i in range(size):
        v = res[i]
        if abs(v) > eps:
            out[i + t*amin] = v
    return out

def dist_scale(A, c):
    """ XXX: not general. Assumes A has integer keys and rounds a*c to the first decimal place. """
    B = {}
    for a in A:
        B[round(10 * a * c)/10] = A[a]
    return B

