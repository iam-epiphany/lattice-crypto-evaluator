# decryption_failure_calculator.py
import importlib
import traceback

def compute_failure_probability(algorithm, recommended_params):
    """
    根据算法和推荐参数调用对应的解密失败概率计算模块
    """

    try:
        module_name = _select_failure_module(algorithm, recommended_params)
        if module_name is None:
            return f"无对应的解密失败概率模块{module_name}"

        failure_module = importlib.import_module(module_name)
        return failure_module.compute_failure_probability(**recommended_params)

    except Exception as e:
        traceback.print_exc()
        return f"调用解密失败概率模块时发生错误: {e}"


def _select_failure_module(algorithm, params):
    """
    根据算法名 + 参数结构，选择正确的 failure 模块
    """
    # =========================
    # NTRU
    # =========================
    if algorithm == "NTRU":
        return "failure.NTRU"
    # =========================
    # LWE
    # =========================
    if algorithm == "LWE":
        return "failure.LWE"

    # =========================
    # RLWE
    # =========================
    if algorithm == "RLWE_2n":
        return "failure.RLWE_2n"
    if algorithm == "RLWE_3n":
            return "failure.RLWE_3n"


    # =========================
    # MLWE
    # =========================
    if algorithm == "MLWE_2n":
        return "failure.MLWE_2n"
    if algorithm == "MLWE_3n":
        return "failure.MLWE_3n"

    # =========================
    # ARLWE（3n）
    # =========================
    if algorithm == "MLWE_ss":
        return "failure.MLWE_X^n-X+1"

    # =========================
    # LWR
    # =========================
    if algorithm == "LWR":
        return "failure.LWR"

    # =========================
    # RLWR
    # =========================
    if algorithm == "RLWR":
        return "failure.RLWR"

    # =========================
    # MLWR
    # =========================
    if algorithm == "MLWR":
        return "failure.MLWR"

    return None
