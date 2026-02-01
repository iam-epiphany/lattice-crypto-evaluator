import math
from .util import *
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from types import SimpleNamespace

# ===============================
# 这里假设噪声是gr+fe，且均服从中心二项分布
# ===============================

# ===============================
# ψ₁ 分布
# ===============================
def psi_1_law():
    psi = build_centered_binomial_law(1)
    return psi

# ===============================
# RLWE-3n 噪声基本项
# ===============================
def build_table1():
    psi = psi_1_law()
    law = defaultdict(float)

    for a1, p1 in psi.items():
        for a2, p2 in psi.items():
            for b1, p3 in psi.items():
                for b2, p4 in psi.items():
                    val = a1*a2 + b1*b2
                    law[val] += p1*p2*p3*p4

    return dict(law)

def build_table2():
    psi = psi_1_law()
    law = defaultdict(float)

    for a1, p1 in psi.items():
        for a2, p2 in psi.items():
            for b1, p3 in psi.items():
                for b2, p4 in psi.items():
                    val = (a1*b1) + b2*(a1 + a2)
                    law[val] += p1*p2*p3*p4
    law = dict(law)
    return law

# ===============================
# RLWE-3n 解密失败概率计算（多进程版）
# ===============================
def _compute_single_i(args):
    """
    单个 i 下的卷积和尾概率计算
    """
    i, n, law1, law2, threshold = args

    # D = law1^(2*i) * law2^(n - 2*i)
    D1 = iter_law_convolution(law1, 2 * i)
    D2 = iter_law_convolution(law2, n - 2 * i)
    D = law_convolution(D1, D2)

    tail_prob = sum(p for x, p in D.items() if abs(x) > threshold)
    return tail_prob

def compute_failure_probability(**params):
    """
    多进程版本：加速卷积部分
    """

    ps = SimpleNamespace(**params)
    n, q = ps.n, ps.q

    # 构建概率分布表
    law1 = build_table1()
    law2 = build_table2()

    threshold = math.floor((q - 3) / 6)

    # 准备参数列表
    args_list = [(i, n, law1, law2, threshold) for i in range(n // 2)]

    log_p_success = 0.0

    # 使用多进程
    with Pool(cpu_count()) as pool:
        tail_probs = pool.map(_compute_single_i, args_list)

    # 累加每个 i 对应的 log(1 - 2*tail_prob)
    for tail_prob in tail_probs:
        log_p_success += math.log1p(-2 * tail_prob)

    # 最后一项 n/2
    D_last = iter_law_convolution(law2, n)
    tail_last = sum(p for x, p in D_last.items() if abs(x) > threshold)
    log_p_success += (n // 2) * math.log1p(-2 * tail_last)

    # 由成功概率计算失败概率
    if log_p_success < 0:
        log2_failure = math.log(-log_p_success, 2)
    else:
        log2_failure = float("-inf")

    return log2_failure

"""
以下是非并行的，原版代码
# ============================================================
# RLWE-3n 解密失败概率计算
# 该方案适用RLWE和RLWR
# ============================================================
def rlwe_3n_failure_probability(ps):
    ""
    参数 ps : ParameterSet
        参数集合，需包含：
            ps.n : 环维度 n
            ps.q : 模数 q

    返回 log_p_success : float
        解密成功概率的自然对数 ln(P_success)

    log2_failure : float
        解密失败概率的以 2 为底的对数 log2(P_failure)
        （当失败概率极小时，使用近似公式计算）
    ""

    n, q = ps.n, ps.q

    # 两类噪声项对应的概率分布表
    # law1：对应 (a1*a2 + b1*b2) 形式的二次项
    # law2：对应 (a1*b1 + b2*(a1+a2)) 形式的二次项
    law1 = build_table1()
    law2 = build_table2()

    # ------------------------------------------------------------
    # 解密阈值
    # 正确判决条件为：
    #     |noise| ≤ floor((q - 3) / 6)
    # 因此失败条件为：
    #     |noise| > floor((q - 3) / 6)
    # ------------------------------------------------------------
    threshold = math.floor((q - 3) / 6)

    # ------------------------------------------------------------
    # 在对数域中累计“解密成功概率”
    #
    # 最终有：
    #   P_success = ∏ (1 - 2 * tail_i)
    # 因此：
    #   ln(P_success) = ∑ ln(1 - 2 * tail_i)
    # ------------------------------------------------------------
    log_p_success = 0.0

    # ------------------------------------------------------------
    # 第一部分：
    # i = 0, 1, ..., n/2 - 1
    #
    # 对应 Sage 代码中的：
    #   for i in range(0, n/2):
    #       p *= (1 - 2*sum)
    # ------------------------------------------------------------
    for i in range(0, n // 2):
        # 计算当前 i 下的噪声分布
        # D = law1^(2i) * law2^(n-2i)
        D1 = iter_law_convolution(law1, 2 * i)
        D2 = iter_law_convolution(law2, n - 2 * i)
        D  = law_convolution(D1, D2)

        # --------------------------------------------------------
        # 计算尾概率：
        #   tail_prob = P(|X| > threshold)
        # --------------------------------------------------------
        tail_prob = 0.0
        for x, p in D.items():
            if abs(x) > threshold:
                tail_prob += p

        # --------------------------------------------------------
        # 更新成功概率的对数
        #
        # 使用 log1p(x) = ln(1+x)，在 x 接近 0 时数值更稳定
        # 这里 x = -2 * tail_prob
        # --------------------------------------------------------
        log_p_success += math.log1p(-2 * tail_prob)

    # ------------------------------------------------------------
    # 第二部分：最后一项
    #
    # 对应 Sage 中的：
    #   p *= (1 - 2*sum)^(n/2)
    # ------------------------------------------------------------
    D_last = iter_law_convolution(law2, n)

    tail_last = 0.0
    for x, p in D_last.items():
        if abs(x) > threshold:
            tail_last += p

    log_p_success += (n // 2) * math.log1p(-2 * tail_last)

    # ------------------------------------------------------------
    # 由成功概率得到失败概率
    #
    # 当失败概率极小时：
    #   P_success = exp(-ε),  ε ≪ 1
    #   P_failure = 1 - exp(-ε) ≈ ε
    #
    # 因此：
    #   log2(P_failure) ≈ log2(-log_p_success)
    # ------------------------------------------------------------
    if log_p_success < 0:
        log2_failure = math.log(-log_p_success, 2)
    else:
        # 理论上不会出现（说明成功概率 ≥ 1）
        log2_failure = float("-inf")

    return log2_failure
"""



"""
修改方法：例如MLWR的r*e+s*e1+e2（这里的e，e1，e2全部由Rounding产生），只需要修改对应的分布即可。
首先计算r*e,table1中的a代表r的独立变量，b代表e的独立变量，假设r服从离散高斯分布，可以改为：
def build_table1(sigma, q, rq):
    # g ~ 离散高斯
    g_dist = build_discrete_gaussian_law(sigma, tail=6)

    # r ~ 模切换误差
    r_dist = build_mod_switching_error_law(q, rq)

    # 构建乘积分布
    law = defaultdict(float)

    for a1, p1 in g_dist.items():
        for a2, p2 in g_dist.items():
            for b1, p3 in r_dist.items():
                for b2, p4 in r_dist.items():
                    val = a1*a2 + b1*b2
                    law[val] += p1*p2*p3*p4

    return dict(law)

def build_table2(sigma, q, rq):
    # g ~ 离散高斯
    g_dist = build_discrete_gaussian_law(sigma, tail=6)

    # r ~ 模切换误差
    r_dist = build_mod_switching_error_law(q, rq)

    for a1, p1 in g_dist.items():
        for a2, p2 in g_dist.items():
            for b1, p3 in r_dist.items():
                for b2, p4 in r_dist.items():
                    val = (a1*b1) + b2*(a1 + a2)
                    law[val] += p1*p2*p3*p4
    law = dict(law)
    return law
上述代码经过函数mlwe_3n_failure_probability的运算即可得到r*e的分布，后续s*e1同理

注意！table1和table2并非分别计算的gr和fe
table1计算的是gr的上半部分，table2计算的是gr的下半部分
只是gr和fe同分布，计算gr后，平方（独立随机变量相加）即可得到gr+fe
"""
