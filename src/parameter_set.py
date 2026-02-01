# Parameter_Set.py

def get_algorithm_params(algorithm_name, eval_type):
    """根据选择的算法和评估类型返回相应的参数"""
    if eval_type == "性能评估":
        if algorithm_name == "NTRU":
            return ["n", "q", "p", "B", "eta"]
        elif algorithm_name == "LWE":
            return ["n", "m", "q", "B", "eta"]
        elif algorithm_name == "RLWE_2n":
            return ["n", "q", "B", "eta"]
        elif algorithm_name == "RLWE_3n":
            return ["n", "q", "B", "eta"]
        elif algorithm_name == "MLWE_2n":
            return ["n", "k", "q", "B", "eta"]
        elif algorithm_name == "MLWE_3n":
            return ["n", "k", "q", "B", "eta"]
        elif algorithm_name == "LWR":
            return ["n", "m", "q", "p", "B", "eta"]
        elif algorithm_name == "RLWR":
            return ["n", "q", "p", "B", "eta"]
        elif algorithm_name == "MLWR":
            return ["n", "k", "p", "q", "B", "eta"]


    elif eval_type == "正确性评估":
        if algorithm_name == "NTRU":
            return ["n", "q"]
        elif algorithm_name == "LWE":
            return ["n", "q", "ks", "ke_pk", "kr", "ke", "threshold"]

        elif algorithm_name == "RLWE_2n":
            return ["n", "ks", "ke", "q", "rqc", "rq2","rqk", "threshold"]

        elif algorithm_name == "MLWE_2n":
            return ["n", "m", "ks", "ke", "ke_ct", "q", "rqk", "rqc", "rq2", "threshold"]

        elif algorithm_name == "RLWE_3n":
            return ["n", "q", "psi_1", "threshold"]

        elif algorithm_name == "MLWE_ss":
            return ["n", "q", "eta_s", "eta_e", "eta_ct", "rqc", "rq2", "threshold"]

        elif algorithm_name == "MLWE_3n":
            return ["n", "q", "k", "psi_1", "rqc", "rq2", "threshold"]

        elif algorithm_name == "LWR":
            return ["n", "q", "p", "ks", "kr", "threshold"]

        elif algorithm_name == "RLWR":
            return ["n", "q", "rqk", "rqc", "rq2", "ks", "kr", "threshold"]

        elif algorithm_name == "MLWR":
            return ["n", "m", "q", "rqk", "rqc", "rq2", "ks", "kr", "threshold"]
    return []
