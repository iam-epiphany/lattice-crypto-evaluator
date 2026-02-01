from .util import *
from types import SimpleNamespace

def lwe_final_error_distribution(ps):
    """
    Compute the final decryption error distribution for standard LWE.
    M = <E,R> - <S,E1> + E2
    """
    # 建立噪声分布
    chis = build_centered_binomial_law(ps.ks)        # s的分布
    chie_pk = build_centered_binomial_law(ps.ke_pk)     # e的分布
    chir = build_centered_binomial_law(ps.kr)        # 临时秘密r的分布
    chie = build_centered_binomial_law(ps.ke)        # 临时噪声e1,e2的分布


    # ----------- 乘积噪声 ① <E, r> -----------
    prod_Er = law_product(chie_pk, chir)
    inner_Er = iter_law_convolution(prod_Er, ps.n)

    # ----------- 乘积噪声 ② <s, e1> -----------
    prod_se = law_product(chis, chie)
    inner_se = iter_law_convolution(prod_se, ps.n)

    # 两个内积噪声相加（减号在对称分布下等价）
    inner_noise = law_convolution(inner_Er, inner_se)

    # ----------- 加性噪声 ③ e2 -----------
    final_error = law_convolution(inner_noise, chie)

    return final_error

def compute_failure_probability(**params):
    ps = SimpleNamespace(**params)
    F = lwe_final_error_distribution(ps)
    proba = tail_probability(F, ps.threshold)
    return log(proba)/log(2)

