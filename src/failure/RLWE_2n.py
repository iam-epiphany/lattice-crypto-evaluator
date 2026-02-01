from .util import *
from types import SimpleNamespace

def rlwe_final_error_distribution(ps):
    """
    构建二次分圆环(X^n+1)基于模2消息编码的MLWE加密方案中最终误差的分布
    :param ps: parameter set (ParameterSet)
    这里假设噪声为r*e-s*(e1+e'')+e2+e'
    """
    if ps.rqk is None:
        ps.rqk = 2 ** ceil(log(ps.q, 2))

    chis = build_centered_binomial_law(ps.ks)           # s的分布
    chie = build_centered_binomial_law(ps.ke)           # e1,e2的分布
    chie_pk = build_centered_binomial_law(ps.ke)        # e的分布
    chir = build_centered_binomial_law(ps.ks)           # r的分布
    Rk = build_mod_switching_error_law(ps.q, ps.rqk)    # 不压缩公钥是0
    Rc = build_mod_switching_error_law(ps.q, ps.rqc)    # u的模切换误差分布
    chiRs = law_convolution(chir, Rk)                   # 公钥不压缩时可以理解为r的分布
    chiRe = law_convolution(chie, Rc)                   # e1+e''

    B1 = law_product(chie_pk, chiRs)                    # e*r
    B2 = law_product(chis, chiRe)                       # (e1+e'')*s

    C1 = iter_law_convolution(B1, ps.n)
    C2 = iter_law_convolution(B2, ps.n)

    C = law_convolution(C1, C2)

    R2 = build_mod_switching_error_law(ps.q, ps.rq2)    # v的模切换误差分布
    F = law_convolution(R2, chie)                       # e2+e'
    D = law_convolution(C, F)                           # Final error
    return D

def compute_failure_probability(**params):
    """
    计算最终误差分布在尾部（超过某个阈值）的概率
    """
    ps = SimpleNamespace(**params)
    F = rlwe_final_error_distribution(ps)
    proba = tail_probability(F, ps.threshold)
    return log(ps.n * proba) / log(2)
