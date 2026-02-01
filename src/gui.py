# gui.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QLineEdit, QPushButton, QTextEdit, QGridLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from parameter_set import get_algorithm_params
from api import evaluate_performance  # 调用接口函数

class CryptoEvaluator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Post-Quantum Crypto Evaluator")
        self.setGeometry(800, 200, 600, 800)
        self.setStyleSheet("background-color: #F5F5F5;")
        self.font = QFont("Arial", 14)
        self.setFont(self.font)

        # 主布局
        self.layout = QVBoxLayout()

        # 标题
        self.title_label = QLabel("格公钥密码算法性能评估工具")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #222222; margin: 15px;")
        self.layout.addWidget(self.title_label)

        # 算法选择
        self.algorithm_label = QLabel("算法类型:")
        self.algorithm_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.algorithm_label.setStyleSheet("color: #333333; margin-top: 10px;")
        self.layout.addWidget(self.algorithm_label)

        self.algorithm_combobox = QComboBox()
        self.algorithm_combobox.addItems(
            ["NTRU", "LWE", "RLWE", "MLWE", "LWR", "RLWR","MLWR"]
        )
        self.algorithm_combobox.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 5px;
            padding: 6px;
            font-size: 16px;
            border: 1px solid #CCCCCC;
        """)
        self.layout.addWidget(self.algorithm_combobox)

        # 环结构选择（仅 MLWE / RLWE 可见）
        self.ring_label = QLabel("环结构:")
        self.ring_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.ring_label.setStyleSheet("color: #333333; margin-top: 10px;")
        self.layout.addWidget(self.ring_label)

        self.ring_combobox = QComboBox()
        self.ring_combobox.addItems([
            "3n次分圆多项式环",
            "2n次分圆多项式环"
        ])
        self.ring_combobox.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 5px;
            padding: 6px;
            font-size: 16px;
            border: 1px solid #CCCCCC;
        """)
        self.layout.addWidget(self.ring_combobox)

        # 默认隐藏
        self.ring_label.hide()
        self.ring_combobox.hide()

        self.eval_type_label = QLabel("评估类型:")
        self.eval_type_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.eval_type_label.setStyleSheet("color: #333333; margin-top: 10px;")
        self.layout.addWidget(self.eval_type_label)

        self.eval_type_combobox = QComboBox()
        self.eval_type_combobox.addItems(["性能评估", "正确性评估"])
        self.eval_type_combobox.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 5px;
            padding: 6px;
            font-size: 16px;
            border: 1px solid #CCCCCC;
        """)
        self.layout.addWidget(self.eval_type_combobox)

        # 新增绑定
        self.eval_type_combobox.currentIndexChanged.connect(self.update_params)

        # 输入参数
        self.input_label = QLabel("输入参数:")
        self.input_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.input_label.setStyleSheet("color: #333333; margin-top:10px;")
        self.layout.addWidget(self.input_label)

        self.param_labels = {}
        self.param_inputs = {}
        self.input_layout = QGridLayout()
        self.layout.addLayout(self.input_layout)

        # 评估按钮
        self.calculate_button = QPushButton("评估")
        self.calculate_button.setFixedHeight(45)
        self.calculate_button.setStyleSheet("""
            background-color: #008C8C;
            color: white;
            border-radius: 6px;
            font-size: 16px;
            padding: 10px;
            font-weight: bold;
            border: none;
        """)
        self.layout.addWidget(self.calculate_button, alignment=Qt.AlignCenter)

        # 输出结果框
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setFixedHeight(300)
        self.result_box.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 6px;
            border: 1px solid #CCCCCC;
            padding: 10px;
            font-size: 16px;
            color: #333333;
        """)
        self.layout.addWidget(self.result_box)

        self.setLayout(self.layout)

        # 事件绑定
        self.algorithm_combobox.currentIndexChanged.connect(self.update_params)
        self.calculate_button.clicked.connect(self.on_calculate_click)
        self.ring_combobox.currentIndexChanged.connect(self.update_params)

        # 默认加载参数
        self.update_params()

    def update_params(self):
        selected_algorithm = self.algorithm_combobox.currentText()

        # 只有 MLWE / RLWE 显示环结构
        if selected_algorithm in ["MLWE", "RLWE"]:
            self.ring_label.show()
            self.ring_combobox.show()
        else:
            self.ring_label.hide()
            self.ring_combobox.hide()

        # 清空旧控件
        for label in self.param_labels.values():
            label.deleteLater()
        for input_field in self.param_inputs.values():
            input_field.deleteLater()
        self.param_labels.clear()
        self.param_inputs.clear()

        # 获取算法 + 评估类型
        selected_algorithm = self.algorithm_combobox.currentText()
        selected_eval_type = self.eval_type_combobox.currentText()

        # 获取参数（你可以在 get_algorithm_params() 中根据评估类型返回不同参数列表）
        real_algorithm = selected_algorithm

        # MLWE / RLWE 需要根据环结构细分
        if selected_algorithm in ["MLWE", "RLWE"]:
            ring_type = self.ring_combobox.currentText()
            if ring_type == "3n次分圆多项式环":
                real_algorithm = f"{selected_algorithm}_3n"
            else:
                real_algorithm = f"{selected_algorithm}_2n"

        params = get_algorithm_params(real_algorithm, selected_eval_type)

        for index, param in enumerate(params):
            row = index % 5
            col = (index // 5) * 2

            label = QLabel(f"{param}:")
            label.setStyleSheet("color: #333333; font-size: 12px; margin-top:5px;")
            self.input_layout.addWidget(label, row, col)

            input_field = QLineEdit()
            input_field.setFixedHeight(35)
            input_field.setStyleSheet("""
                background-color: #FFFFFF;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
                border: 1px solid #CCCCCC;
            """)
            self.input_layout.addWidget(input_field, row, col + 1)

            self.param_labels[param] = label
            self.param_inputs[param] = input_field

    def on_calculate_click(self):
        # 重新获取算法和评估类型的最新选项
        selected_algorithm = self.algorithm_combobox.currentText()
        real_algorithm = selected_algorithm

        if selected_algorithm in ["MLWE", "RLWE"]:
            ring_type = self.ring_combobox.currentText()
            if ring_type == "3n次分圆多项式环":
                real_algorithm = f"{selected_algorithm}_3n"
            else:
                real_algorithm = f"{selected_algorithm}_2n"

        selected_eval_type = self.eval_type_combobox.currentText()

        # 获取对应的参数
        param_names = get_algorithm_params(real_algorithm, selected_eval_type)
        params_list = []
        for param in param_names:
            params_list.append(self.param_inputs[param].text().strip())
        # 调用评估函数
        result = evaluate_performance(real_algorithm, params_list, selected_eval_type)

        # 显示评估结果
        self.result_box.setText(f"评估结果：\n{result}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = CryptoEvaluator()
    window.show()
    sys.exit(app.exec_())
