from .util import *
from types import SimpleNamespace

def rlwr_final_error_distribution(ps):
    """
    构建二次分圆环(X^n+1)基于模2消息编码的RLWR加密方案中最终误差的分布
    :param ps: parameter set (ParameterSet) - 需要包含MLWR特定的参数
    """
    # MLWR中没有LWE误差分布，只有模切换误差
    s = build_centered_binomial_law(ps.ks)  # 密钥s的分布

    # MLWR中的误差来源：
    # 1. 公钥生成时的模约简误差
    e = build_mod_switching_error_law(ps.q, ps.rqk)  # 公钥模约简误差
    re = law_product(s,e)

    # 计算
    D1 = iter_law_convolution(re, ps.n)

    # 2. 密文生成时的模约简误差
    e1 = build_mod_switching_error_law(ps.q, ps.rqc)  # 第一密文分量u的模约简误差
    re1 = law_product(s,e1)

    D2 = iter_law_convolution(re1, ps.n)

    D = law_convolution(D1, D2)

    e2 = build_mod_switching_error_law(ps.q, ps.rq2)  # 第二密文分量v的模约简误差

    D = law_convolution(D, e2)

    return D


def compute_failure_probability(**params):
    """
    计算MLWR最终误差分布在尾部（超过某个阈值）的概率
    """
    ps = SimpleNamespace(**params)
    F = rlwr_final_error_distribution(ps)
    proba = tail_probability(F, ps.threshold)
    return log(ps.n * proba) / log(2)