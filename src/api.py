from parameter_set import get_algorithm_params
from size_calculator import calculate_dimensions, parse_input
from time_calculator import calculate_time
from decryption_failure_calculator import compute_failure_probability
from utils import process_params

def evaluate_performance(algorithm: str, params: list, eval_type: str) -> str:
    """
    接口函数：根据算法名称、参数列表和评估类型，执行对应的评估逻辑。

    参数:
      algorithm: 算法名称
      params: 参数值列表，与 get_algorithm_params 返回的顺序一致
      eval_type: 评估类型，可为 "性能评估" 或 "正确性评估"

    返回:
      一个字符串，包含选择的评估类型下对应内容。
    """
    try:
        processed_params = process_params(params)
    except Exception as e:
        return f"参数处理错误: {e}"

    param_names = get_algorithm_params(algorithm, eval_type)

    input_params = {name: value for name, value in zip(param_names, processed_params)}
    result_text = ""

    # === 性能评估 ===
    if eval_type == "性能评估":
        try:
            if algorithm == "NTRU":
                modq_size, short_size_1, public_key_size, private_key_size, ciphertext_size = calculate_dimensions(algorithm, input_params)
                result_text += (
                    "通信开销评估：\n"
                    f"模q多项式/向量尺寸：{modq_size} bytes\n"
                    f"短多项式/向量尺寸：{short_size_1} bytes\n"
                    f"公钥尺寸: {public_key_size} bytes\n"
                    f"私钥尺寸: {private_key_size} bytes\n"
                    f"密文尺寸: {ciphertext_size} bytes\n"
                )
            else:
                modq_size, short_size_1, public_key_size, private_key_size, ciphertext_size, short_size_2 = calculate_dimensions(algorithm, input_params)
                result_text += (
                    "通信开销评估：\n"
                    f"模q多项式/向量尺寸：{modq_size} bytes\n"
                    f"短多项式/向量尺寸(均匀分布)：{short_size_1} bytes\n"
                    f"短多项式/向量尺寸(中心二项分布): {short_size_2} bytes\n"
                    f"公钥尺寸: {public_key_size} bytes\n"
                    f"私钥尺寸: {private_key_size} bytes\n"
                    f"密文尺寸: {ciphertext_size} bytes\n"
                )
        except Exception as e:
            result_text += f"计算通信开销时发生错误: {e}\n"

        try:
            time_output = calculate_time(algorithm, input_params)
            result_text += f"\n时间性能评估:\n{time_output}\n"
        except Exception as e:
            result_text += f"\n时间性能评估时发生错误: {e}\n"

    # === 正确性评估 ===
    elif eval_type == "正确性评估":
        try:
            failure_prob_output = compute_failure_probability(algorithm, input_params)
            result_text += f"\n解密失败概率评估:\n2^({failure_prob_output})\n"
        except Exception as e:
            result_text += f"计算解密失败概率时发生错误: {e}\n"

    else:
        result_text = "错误：未知的评估类型（请使用 '性能评估' 或 '正确性评估'）"

    return result_text
