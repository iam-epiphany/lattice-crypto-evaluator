from .util import *
from types import SimpleNamespace

def mlwe_final_error_distribution(ps):
    """
    构建二次分圆环 (X^n+1) 上、模 2 消息编码的 MLWE 加密方案最终误差分布
    噪声模型：r*e - s*(e1+e'') + e2 + e'
    """
    if ps.ke_ct is None:
        ps.ke_ct = ps.ke
    if ps.rqk is None:
        ps.rqk = 2 ** ceil(log(ps.q, 2))

    # ===============================
    # 基础噪声分布
    # ===============================
    dist_s  = build_centered_binomial_law(ps.ks)        # s
    dist_e1 = build_centered_binomial_law(ps.ke_ct)     # e1, e2
    dist_ep = build_centered_binomial_law(ps.ke)        # e
    dist_r  = build_centered_binomial_law(ps.ks)        # r

    # ===============================
    # 模切换误差分布
    # ===============================
    err_pk = build_mod_switching_error_law(ps.q, ps.rqk)   # 公钥模切换（不压缩为 0）
    err_u  = build_mod_switching_error_law(ps.q, ps.rqc)   # u 的模切换误差

    # ===============================
    # 合成中间分布
    # ===============================
    law_r_eff  = law_convolution(dist_r, err_pk)           # r + rounding
    law_e_eff  = law_convolution(dist_e1, err_u)           # e1 + e''

    # ===============================
    # 核心乘积项
    # ===============================
    term_re = law_product(dist_ep, law_r_eff)              # e * r
    term_se = law_product(dist_s,  law_e_eff)              # s * (e1+e'')

    # ===============================
    # n·m 次累加
    # ===============================
    acc_re = iter_law_convolution(term_re, ps.m * ps.n)
    acc_se = iter_law_convolution(term_se, ps.m * ps.n)

    mix_core = law_convolution(acc_re, acc_se)

    # ===============================
    # 最终误差项
    # ===============================
    err_v = build_mod_switching_error_law(ps.q, ps.rq2)    # v 的模切换误差
    tail  = law_convolution(err_v, dist_e1)                # e2 + e'

    final_law = law_convolution(mix_core, tail)

    return final_law


def compute_failure_probability(**params):
    """
    计算最终误差超过阈值的失败概率（以 log2 表示）
    """
    ps = SimpleNamespace(**params)
    err_dist = mlwe_final_error_distribution(ps)
    fail_p   = tail_probability(err_dist, ps.threshold)

    return log(ps.n * fail_p) / log(2)
