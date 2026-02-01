from .util import *
from types import SimpleNamespace

# ============================================================
# LWR 最终解密误差分布
# ============================================================
def lwr_final_error_distribution(ps):
    """
    计算标准 LWR 的最终解密误差分布

    在 LWR 中不存在显式噪声 e，
    所有噪声均来源于模数切换（取整）误差。

    误差模型：
        M = <ε_E, r> - <s, ε_E1> + ε_E2
    """

    q  = ps.q          # 原模数
    rq = ps.p         # 压缩模数（如 p）

    chis = build_centered_binomial_law(ps.ks)  # s的分布
    chir = build_centered_binomial_law(ps.kr)  # 临时秘密r的分布

    # --------------------------------------------------------
    # 模数切换误差分布（LWR 的“噪声分布”）
    # --------------------------------------------------------
    chi_ms = build_mod_switching_error_law(q, rq)

    # --------------------------------------------------------
    # ① <ε_E, r>
    # r 在 LWR 中是均匀的，但只通过取整误差进入
    # 因此 r 对应的噪声仍然是 chi_ms
    # --------------------------------------------------------
    prod_Er = law_product(chi_ms, chir)
    inner_Er = iter_law_convolution(prod_Er, ps.n)

    # --------------------------------------------------------
    # ② <s, ε_E1>
    # s 是均匀秘密，但误差仍由取整产生
    # --------------------------------------------------------
    prod_se = law_product(chi_ms, chis)
    inner_se = iter_law_convolution(prod_se, ps.n)

    # 内积噪声合并（减号在对称分布下等价）
    inner_noise = law_convolution(inner_Er, inner_se)

    # --------------------------------------------------------
    # ③ 加性模数切换误差 ε_E2
    # --------------------------------------------------------
    final_error = law_convolution(inner_noise, chi_ms)

    return final_error


# ============================================================
# LWR 解密失败概率
# ============================================================
def compute_failure_probability(**params):
    """
    计算 LWR 解密失败概率
    """
    ps = SimpleNamespace(**params)
    F = lwr_final_error_distribution(ps)

    # 判决阈值与 LWE 类似，只是参数来源不同
    proba = tail_probability(F, ps.threshold)

    return log(proba)/log(2)
