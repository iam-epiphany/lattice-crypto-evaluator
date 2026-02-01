# time_calculator.py
import math

from utils import parse_input, ceil_log2, uniform_len


def calculate_time(algorithm, params):
    """
    param_dict: 参数字典，如 { 'n': '512', 'q': '3329', 'B': '128', ... }
    algorithm_name: 算法名称，如 "NTRU", "LWE", "MLWE", "RLWE", "LWR", "MLWR", "RLWR"

    返回：
    一个格式化字符串，展示密钥生成、加密、解密的时间（单位 ms）
    """

    T_shake = "次SHAKE256"
    T_mutiple = "次乘法"
    try:
        # NTRU: 参数 n, B, eta
        if algorithm == "NTRU":
            n = parse_input(params["n"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            keygen_time_sample_1 = math.ceil(2 * (n * uniform_len(B) / 136))
            keygen_time_sample_2 = math.ceil(2 * (n * eta / 4 / 136))
            keygen_time_compute = 2 * 5 * n * n + n * n
            encrypt_time_1 = math.ceil((n * uniform_len(B) / 8) / 136)
            encrypt_time_2 = math.ceil((n * eta / 4) / 136)
            decrypt_time = n * n
            result = ("均匀分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_1}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_1}{T_shake}+{n * n}{T_mutiple}\n"
                      f"解密耗时：{n * n}{T_mutiple}\n"
                      "中心二项分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_2}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_2}{T_shake}+{n * n}{T_mutiple}\n"
                      f"解密耗时：{decrypt_time}{T_mutiple}\n")

        # LWE: 参数 n, m, q, B, eta
        elif algorithm == "LWE":
            n = parse_input(params["n"])
            m = parse_input(params["m"])
            q = parse_input(params["q"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            keygen_time_sample_1 = math.ceil(m*n*ceil_log2(q)/8/136 + (n+m) * uniform_len(B)/ 136)
            keygen_time_sample_2 = math.ceil(m*n*ceil_log2(q)/8/136 + (m+n)*eta/4/ 136)
            keygen_time_compute = m*n
            encrypt_time_1 = math.ceil((n+m) * uniform_len(B)/136)
            encrypt_time_2 = math.ceil(((n+m) * eta / 4) / 136)
            decrypt_time = n
            result = ("均匀分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_1}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_1}{T_shake}+{2 * m * n}{T_mutiple}\n"
                      f"解密耗时：{n * n}{T_mutiple}\n"
                      "中心二项分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_2}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_2}{T_shake}+{2 * m * n}{T_mutiple}\n"
                      f"解密耗时：{decrypt_time}{T_mutiple}\n")

        # RLWE: 参数 n, q, B, eta
        elif algorithm == "RLWE":
            n = parse_input(params["n"])
            q = parse_input(params["q"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            keygen_time_sample_1 = math.ceil(3 * (n * uniform_len(B) / 136))
            keygen_time_sample_2 = math.ceil(3 * (n * eta / 4 / 136))
            keygen_time_compute = math.ceil(3 * n * math.log2(n) + n)
            encrypt_time_1 = math.ceil(3*(n * uniform_len(B) / 8 / 136))
            encrypt_time_2 = math.ceil(3*(n * eta / 4 / 136))
            decrypt_time = 3*n*math.log2(n) + n
            result = ("均匀分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_1}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_1}{T_shake}+{2*keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{n * n}{T_mutiple}\n"
                      "中心二项分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_2}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_2}{T_shake}+{2*keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{decrypt_time}{T_mutiple}\n")

        # MLWE: 参数 n, k, q, B, eta
        elif algorithm == "MLWE":
            n = parse_input(params["n"])
            k = parse_input(params["k"])
            q = parse_input(params["q"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            keygen_time_sample_1 = math.ceil(n * k*k * ceil_log2(q)/8/136 + 2 * (n * k * uniform_len(B) / 136))
            keygen_time_sample_2 = math.ceil(n * k*k * ceil_log2(q)/8/136 + 2 * (n * k * eta / 4 / 136))
            keygen_time_compute = k*k*n*math.log2(n)+2*k*n*math.log2(n)+k*k*n
            encrypt_time_1 = math.ceil(3 * (n * k * uniform_len(B) / 8 / 136))
            encrypt_time_2 = math.ceil(3 * (n * k * eta / 4 / 136))
            decrypt_time = 3 * k * n * math.log2(n) + k * n
            result = ("均匀分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_1}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_1}{T_shake}+{2*keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{n * n}{T_mutiple}\n"
                      "中心二项分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_2}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_2}{T_shake}+{2*keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{decrypt_time}{T_mutiple}\n")

        # LWR: 参数 n, m, q, p, B, eta
        elif algorithm == "LWR":
            n = parse_input(params["n"])
            m = parse_input(params["m"])
            q = parse_input(params["q"])
            p = parse_input(params["p"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            keygen_time_sample_1 = math.ceil(n*m*ceil_log2(q)/8/136 + n * uniform_len(B) / 136)
            keygen_time_sample_2 = math.ceil(n*m*ceil_log2(q)/8/136 + (n * eta / 4) / 136)
            keygen_time_compute = n*m
            encrypt_time_1 = math.ceil(n * uniform_len(B) / 8 / 136)
            encrypt_time_2 = math.ceil((n * eta / 4) / 136)
            decrypt_time = n
            result = ("均匀分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_1}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_1}{T_shake}+{2*keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{n * n}{T_mutiple}\n"
                      "中心二项分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_2}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_2}{T_shake}+{2*keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{decrypt_time}{T_mutiple}\n")

        # RLWR: 参数 n, q, p, B, eta
        elif algorithm == "RLWR":
            n = parse_input(params["n"])
            q = parse_input(params["q"])
            p = parse_input(params["p"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            keygen_time_sample_1 = math.ceil(2 * (n * uniform_len(B) / 136))
            keygen_time_sample_2 = math.ceil(2 * (n * eta / 4 / 136))
            keygen_time_compute = 3 * n * math.log2(n) + n
            encrypt_time_1 = math.ceil((n * uniform_len(B) / 8) / 136)
            encrypt_time_2 = math.ceil((n * eta / 4) / 136)
            decrypt_time = 3 * n * math.log2(n) + n
            result = ("均匀分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_1}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_1}{T_shake}+{2*keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{n * n}{T_mutiple}\n"
                      "中心二项分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_2}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_2}{T_shake}+{2*keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{decrypt_time}{T_mutiple}\n")

        # MLWR: 参数 n, k, q, p, B, eta
        elif algorithm == "MLWR":
            n = parse_input(params["n"])
            k = parse_input(params["k"])
            q = parse_input(params["q"])
            p = parse_input(params["p"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            keygen_time_sample_1 = math.ceil(n * k * k * ceil_log2(q) / 8 / 136 + (n * k * uniform_len(B) / 136))
            keygen_time_sample_2 = math.ceil(n * k * k * ceil_log2(q) / 8 / 136 + (n * k * eta / 4 / 136))
            keygen_time_compute = k * k * n * math.log2(n) + 2 * k * n * math.log2(n) + k * k * n
            encrypt_time_1 = math.ceil(n * k * uniform_len(B) / 8 / 136)
            encrypt_time_2 = math.ceil(n * k * eta / 4 / 136)
            decrypt_time = 3 * k * n * math.log2(n) + k * n
            result = ("均匀分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_1}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_1}{T_shake}+{2 * keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{n * n}{T_mutiple}\n"
                      "中心二项分布采样耗时：\n"
                      f"密钥生成耗时：{keygen_time_sample_2}{T_shake}+{keygen_time_compute}{T_mutiple}\n"
                      f"加密耗时：{encrypt_time_2}{T_shake}+{2 * keygen_time_compute}{T_mutiple}\n"
                      f"解密耗时：{decrypt_time}{T_mutiple}\n")

        else:
            raise ValueError("Unsupported algorithm")

        return result

    except Exception as e:
        return f"计算错误：{str(e)}"
