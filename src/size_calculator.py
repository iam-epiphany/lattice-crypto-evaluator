# size_calculator.py
import math
from utils import parse_input, ceil_log2

def calculate_dimensions(algorithm, params):
    try:
        # NTRU: 参数 n, q, p
        if algorithm == "NTRU":
            n = parse_input(params["n"])
            q = parse_input(params["q"])
            p = parse_input(params["p"])
            public_key_size = n * ceil_log2(q) / 8
            private_key_size = n * ceil_log2(q) / 8 + 2 * n * ceil_log2(p) / 8
            ciphertext_size = public_key_size
            modq_size = n * ceil_log2(q) / 8
            short_size_1 = n * ceil_log2(q) / 8
            short_size_2 = n * ceil_log2(q) / 8

        # LWE: 参数 n, m, q, B, eta
        elif algorithm == "LWE":
            n = parse_input(params["n"])
            m = parse_input(params["m"])
            q = parse_input(params["q"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            public_key_size = m * ceil_log2(q) / 8 + 16
            private_key_size = n * ceil_log2(q) / 8
            ciphertext_size = (n+1) * ceil_log2(q) / 8
            modq_size = n * ceil_log2(q) / 8
            short_size_1 = n * ceil_log2(2*B+1)*(B/2**ceil_log2(B)) / 8
            short_size_2 = 2 * n * eta / 8

        # RLWE: 参数 n, q, B, eta
        elif algorithm == "RLWE":
            n = parse_input(params["n"])
            q = parse_input(params["q"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            public_key_size = 2 * n * ceil_log2(q) / 8
            private_key_size = n * ceil_log2(q) / 8
            ciphertext_size = (n+1) * ceil_log2(q) / 8
            modq_size = n * ceil_log2(q) / 8
            short_size_1 = n * ceil_log2(2*B+1)*(B/2**ceil_log2(B)) / 8
            short_size_2 = 2 * n * eta / 8

        # MLWE: 参数 n, k, q, B, eta
        elif algorithm == "MLWE":
            n = parse_input(params["n"])
            k = parse_input(params["k"])
            q = parse_input(params["q"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            public_key_size = k * n * math.log2(q) / 8 + 32
            private_key_size = k * n * math.log2(q) / 8
            ciphertext_size = (k+1) * n * math.log2(q) / 8
            modq_size = n * ceil_log2(q) / 8
            short_size_1 = n * k * ceil_log2(2*B+1)*(B/2**ceil_log2(B)) / 8
            short_size_2 = 2 * n * k * eta / 8

        # LWR: 参数 n, m, q, p, B, eta
        elif algorithm == "LWR":
            n = parse_input(params["n"])
            m = parse_input(params["m"])
            q = parse_input(params["q"])
            p = parse_input(params["p"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            public_key_size = m * ceil_log2(p) / 8 + 16
            private_key_size = n * ceil_log2(q) / 8
            ciphertext_size = (n+1) * ceil_log2(p) / 8
            modq_size = n * ceil_log2(q) / 8
            short_size_1 = n * ceil_log2(2*B+1)*(B/2**ceil_log2(B)) / 8
            short_size_2 = 2 * n * eta / 8

        # RLWR: 参数 n, q, p, B, eta
        elif algorithm == "RLWR":
            n = parse_input(params["n"])
            q = parse_input(params["q"])
            p = parse_input(params["p"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            public_key_size = n * ceil_log2(p) / 8 + n * ceil_log2(q) / 8
            private_key_size = n * ceil_log2(q) / 8
            ciphertext_size = 2 * n * ceil_log2(p) / 8
            modq_size = n * ceil_log2(q) / 8
            short_size_1 = n * ceil_log2(2*B+1)*(B/2**ceil_log2(B)) / 8
            short_size_2 = 2 * n * eta / 8

        # MLWR: 参数 n, k, q, p, B, eta
        elif algorithm == "MLWR":
            n = parse_input(params["n"])
            k = parse_input(params["k"])
            q = parse_input(params["q"])
            p = parse_input(params["p"])
            B = parse_input(params["B"])
            eta = parse_input(params["eta"])
            public_key_size = k * n * ceil_log2(p) / 8 + 32
            private_key_size = k * n * ceil_log2(q) / 8
            ciphertext_size = (k+1) * n * ceil_log2(p) / 8
            modq_size = n * ceil_log2(q) / 8
            short_size_1 = n * ceil_log2(2*B+1)*(B/2**ceil_log2(B)) / 8
            short_size_2 = 2 * n * eta / 8

        else:
            raise ValueError("Unsupported algorithm")
        if algorithm=="NTRU":
            return int(modq_size), int(short_size_1), int(public_key_size), int(private_key_size), int(ciphertext_size)
        elif algorithm!="NTRU":
            return int(modq_size), int(short_size_1), int(public_key_size), int(private_key_size), int(ciphertext_size), int(short_size_2)

    except Exception as e:
        return f"计算错误：{str(e)}"
