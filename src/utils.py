#utils.py
import math
def parse_input(value):
    if not isinstance(value, str):
        return value
    try:
        value = value.strip()
        # 检查是否是 2^n 或 ** 格式
        if '^' in value:
            base, exponent = value.split('^')
            result = float(base.strip()) ** int(exponent.strip())
        elif '**' in value:
            base, exponent = value.split('**')
            result = float(base.strip()) ** int(exponent.strip())
        else:
            result = float(value)  # 通用数字转换
        # 如果结果小数部分为0，则返回整数
        if isinstance(result, float) and result.is_integer():
            return int(result)
        return result
    except ValueError:
        raise ValueError(f"无效输入: {value}. ")

def process_params(params: list) -> list:
    """
    处理输入的参数列表：
      - 如果参数为字符串（不论是否包含 '^' 或 '**'），调用 parse_input 进行转换；
      - 非字符串参数若为整数或浮点数则保留原类型（必要时转换为 float）；
    转换后如果数值为整数（即小数部分为0）则返回整数，否则返回浮点数。
    """
    processed = []
    for p in params:
        # 如果是字符串，调用 parse_input 处理
        if isinstance(p, str):
            try:
                value = parse_input(p)
            except Exception as e:
                raise ValueError(f"参数 {p} 格式错误: {e}")
        # 如果是整数，直接保留
        elif isinstance(p, int):
            value = p
        # 如果是浮点数，直接保留
        elif isinstance(p, float):
            value = p
        else:
            try:
                value = float(p)
            except Exception as e:
                raise ValueError(f"参数 {p} 不能转换为数值: {e}")

        # 判断转换后的数值是否为整数（小数部分为0）
        if isinstance(value, float) and value.is_integer():
            processed.append(int(value))
        else:
            processed.append(value)
    return processed

def ceil_log2(x):
    """返回 ⌈log₂(x)⌉"""
    return math.ceil(math.log2(x))

def uniform_len(B):
    return ceil_log2(B) * (B / 2 ** ceil_log2(B)) / 8