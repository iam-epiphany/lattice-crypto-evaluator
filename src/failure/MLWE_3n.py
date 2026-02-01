import math
from .util import *
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from types import SimpleNamespace

# 噪声为r*e-s*(e1+e'')+e2+e'


# ===============================
# RLWE-3n 噪声基本项r*e
# ===============================
# c'
def build_re_table1(sigma):
    print("[ENTER] build_re_table1, sigma =", sigma)
    # e ~ 离散高斯
    e_dist = build_discrete_gaussian_law(sigma)  #[-6,6]
    # r ~ 离散高斯
    r_dist = build_discrete_gaussian_law(sigma)

    # 构建乘积分布
    law = defaultdict(float)

    for a1, p1 in e_dist.items():
        for a2, p2 in e_dist.items():
            for b1, p3 in r_dist.items():
                for b2, p4 in r_dist.items():
                    val = a1 * a2 + b1 * b2
                    law[val] += p1 * p2 * p3 * p4

    return dict(law)

# c
def build_re_table2(sigma):
    print("[ENTER] build_re_table2, sigma =", sigma)
    # e ~ 离散高斯
    e_dist = build_discrete_gaussian_law(sigma)
    # r ~ 离散高斯
    r_dist = build_discrete_gaussian_law(sigma)

    law = defaultdict(float)

    for a1, p1 in e_dist.items():
        for a2, p2 in e_dist.items():
            for b1, p3 in r_dist.items():
                for b2, p4 in r_dist.items():
                    val = (a1 * b1) + b2 * (a1 + a2)
                    law[val] += p1 * p2 * p3 * p4
    law = dict(law)
    return law


# ===============================
# RLWE-3n 噪声基本项s*(e1+e'')
# ===============================
def build_se_table1(sigma, q, rq):
    print("[ENTER] build_se_table1")
    # s ~ 离散高斯
    s_dist = build_discrete_gaussian_law(sigma)
    # e1 ~ 离散高斯
    e1_dist = build_discrete_gaussian_law(sigma)
    # e'' ~ rounding 噪声
    Rc_dist = build_mod_switching_error_law(q,rq)  #[-floor(q/2*rq),floor(q/2*rq)]
    # e1+e''
    Re_dist = law_convolution(e1_dist, Rc_dist)

    # 构建乘积分布
    law = defaultdict(float)

    for a1, p1 in s_dist.items():
        for a2, p2 in s_dist.items():
            for b1, p3 in Re_dist.items():
                for b2, p4 in Re_dist.items():
                    val = a1 * a2 + b1 * b2
                    law[val] += p1 * p2 * p3 * p4

    return dict(law)


def build_se_table2(sigma, q, rq):
    print("[ENTER] build_se_table2")
    # s ~ 离散高斯
    s_dist = build_discrete_gaussian_law(sigma)
    # e1 ~ 离散高斯
    e1_dist = build_discrete_gaussian_law(sigma)
    # e'' ~ rounding 噪声
    Rc_dist = build_mod_switching_error_law(q, rq)
    # e1+e''
    Re_dist = law_convolution(e1_dist, Rc_dist)

    law = defaultdict(float)

    for a1, p1 in s_dist.items():
        for a2, p2 in s_dist.items():
            for b1, p3 in Re_dist.items():
                for b2, p4 in Re_dist.items():
                    val = (a1 * b1) + b2 * (a1 + a2)
                    law[val] += p1 * p2 * p3 * p4

    return dict(law)

# ===============================
# 多进程调用的循环部分
# ===============================
def _compute_single_i(args):
    i, n, k, threshold, law1, law2, law3, law4, D_lin = args

    D_re1 = iter_law_convolution(law1, i * k)
    D_re2 = iter_law_convolution(law2, (n // 2 - i) * k)
    D_re = law_convolution(D_re1, D_re2)

    D_se1 = iter_law_convolution(law3, i * k)
    D_se2 = iter_law_convolution(law4, (n // 2 - i) * k)
    D_se = law_convolution(D_se1, D_se2)

    D = law_convolution(D_re, D_se)
    D = law_convolution(D, D_lin)

    tail_prob = 0.0
    for x, p in D.items():
        if abs(x) > threshold:
            tail_prob += p

    return math.log1p(-2 * tail_prob)

# ============================================================
# MLWE-3n 解密失败概率计算
# ============================================================
def compute_failure_probability(**params):
    """
    参数 ps : ParameterSet
        参数集合，需包含：
            ps.n : 环维度 n
            ps.q : 模数 q

    返回 log_p_success : float
        解密成功概率的自然对数 ln(P_success)

    log2_failure : float
        解密失败概率的以 2 为底的对数 log2(P_failure)
        （当失败概率极小时，使用近似公式计算）
    """
    print("[ENTER] mlwe_3n_failure_probability")
    ps = SimpleNamespace(**params)
    n, q, k, threshold = ps.n, ps.q, ps.k, ps.threshold
    sigma = ps.psi_1
    rqc, rq2 = ps.rqc, ps.rq2

    # 两类噪声项对应的概率分布表
    # law1：对应 (a1*a2 + b1*b2) 形式的二次项
    # law2：对应 (a1*b1 + b2*(a1+a2)) 形式的二次项
    law1 = build_re_table1(sigma)
    law2 = build_re_table2(sigma)
    law3 = build_se_table1(sigma,q,rqc)
    law4 = build_se_table2(sigma,q,rqc)

    e2_dist = build_discrete_gaussian_law(sigma)
    ep_dist = build_mod_switching_error_law(q, rq2)
    D_lin = law_convolution(e2_dist, ep_dist)

    # ------------------------------------------------------------
    # 第一部分：
    # i = 0, 1, ..., n/2 - 1
    #
    # 对应 Sage 代码中的：
    #   for i in range(0, n/2):
    #       p *= (1 - 2*sum)
    # ------------------------------------------------------------
    args = [
        (i, n, k, threshold, law1, law2, law3, law4, D_lin)
        for i in range(0, n // 2)
    ]

    log_p_success = 0.0

    #这部分改为多进程加速运行
    with Pool(processes=cpu_count()) as pool:
        for cnt, val in enumerate(
                pool.imap_unordered(_compute_single_i, args), 1
        ):
            log_p_success += val
            print(f"[PROGRESS] finished {cnt}/{n // 2}")

    # ------------------------------------------------------------
    # 第二部分：最后一项
    #
    # 对应 Sage 中的：
    #   p *= (1 - 2*sum)^(n/2)
    # ------------------------------------------------------------

    # 计算r*e的c^(n/2),得到r*e下半部分每一个元素的分布
    D_re_last = iter_law_convolution(law2, n // 2 * k)

    # 计算s*(e1+e'')的c^(n/2)，得到s*(e1+e'')下半部分每一个元素的分布
    D_se_last = iter_law_convolution(law4, n // 2 * k)

    # 计算r*e+s*(e1+e'')的下半部分每一个元素的分布
    D_mul_last = law_convolution(D_re_last, D_se_last)

    # 计算r*e+s*(e1+e'')+（e2+e'）的下半部分每一个元素的分布
    D_last = law_convolution(D_mul_last, D_lin)

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
修改方法：例如MLWR的r*e+s*e1+e2（这里的e，e1，e2全部由Rounding产生），只需要修改对应的分布即可。
首先计算r*e,table1中的a代表r的独立变量，b代表e的独立变量，假设r服从离散高斯分布，可以改为：
def build_table1(sigma, q, rq):
    # g ~ 离散高斯
    g_dist = build_discrete_gaussian_law(sigma)

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
    g_dist = build_discrete_gaussian_law(sigma)

    # r ~ 模切换误差
    r_dist = build_mod_switching_error_law(q, rq)
    law = defaultdict(float)
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