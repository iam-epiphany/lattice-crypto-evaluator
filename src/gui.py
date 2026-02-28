# gui.py — 仅负责布局与交互逻辑，样式全部来自 styles.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QLineEdit, QPushButton, QTextEdit, QGridLayout, QFrame,
    QScrollArea, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
import sys

from parameter_set import get_algorithm_params
from api import evaluate_performance
from styles import (
    BG, CARD_BG, BORDER, ACCENT, TEXT_MAIN, TEXT_SUB,
    FONT_BODY, FONT_BOLD, FONT_TITLE, FONT_SUB, FONT_MONO,
    CARD_STYLE, COMBO_STYLE, INPUT_STYLE, BUTTON_STYLE,
    RESULT_STYLE, SCROLL_STYLE, HEADER_STYLE, DIVIDER_STYLE,
    BADGE_READY, BADGE_RUNNING, BADGE_DONE,
    add_shadow
)


# ── 可复用小组件 ──────────────────────────────────────────────────

class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)


class SectionTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(FONT_BOLD)


class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setStyleSheet(DIVIDER_STYLE)


class StatusBadge(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(FONT_SUB)
        self.set_ready()

    def set_ready(self):
        self.setText("  就绪  ")
        self.setStyleSheet(BADGE_READY)

    def set_running(self):
        self.setText("  运行中…  ")
        self.setStyleSheet(BADGE_RUNNING)

    def set_done(self):
        self.setText("  完成 ✓  ")
        self.setStyleSheet(BADGE_DONE)


# ── 主窗口 ────────────────────────────────────────────────────────

class CryptoEvaluator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Post-Quantum Crypto Evaluator")
        self.setGeometry(500, 60, 1000, 1300)   # 更大的默认窗口
        self.setMinimumSize(780, 800)
        self.setStyleSheet(f"background-color: {BG};")
        self.setFont(FONT_BODY)

        self._setup_scroll()
        self._build_header()
        self._build_config_card()
        self._build_params_card()
        self._build_button()
        self._build_result_card()
        self.main.addStretch()

        # 事件绑定
        self.algorithm_combobox.currentIndexChanged.connect(self.update_params)
        self.ring_combobox.currentIndexChanged.connect(self.update_params)
        self.eval_type_combobox.currentIndexChanged.connect(self.update_params)
        self.calculate_button.clicked.connect(self.on_calculate_click)

        self.update_params()

    # ── 滚动区域初始化 ────────────────────────────────────────────

    def _setup_scroll(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(SCROLL_STYLE)

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG};")
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.main = QVBoxLayout(container)
        self.main.setContentsMargins(32, 32, 32, 32)
        self.main.setSpacing(22)

    # ── UI 构建 ───────────────────────────────────────────────────

    def _build_header(self):
        header = QWidget()
        header.setStyleSheet(HEADER_STYLE)
        layout = QVBoxLayout(header)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(8)

        title = QLabel("格公钥密码算法性能评估工具")
        title.setFont(FONT_TITLE)
        title.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title)

        sub = QLabel("Post-Quantum Cryptography · Performance & Correctness Evaluation")
        sub.setFont(FONT_SUB)
        sub.setStyleSheet("color: rgba(255,255,255,0.78);")
        layout.addWidget(sub)

        add_shadow(header, r=24, c="#93C5FD", dy=5)
        self.main.addWidget(header)

    def _build_config_card(self):
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(18)

        # 算法 + 评估类型（并排）
        row = QHBoxLayout()
        row.setSpacing(20)
        row.addLayout(self._labeled_combo("算法类型",
            ["NTRU", "LWE", "RLWE", "MLWE", "LWR", "RLWR", "MLWR"],
            "algorithm_combobox"))
        row.addLayout(self._labeled_combo("评估类型",
            ["性能评估", "正确性评估"],
            "eval_type_combobox"))
        layout.addLayout(row)

        # 环结构（按需显示）
        self.ring_widget = QWidget()
        self.ring_widget.setStyleSheet("background: transparent;")
        rw = QVBoxLayout(self.ring_widget)
        rw.setContentsMargins(0, 0, 0, 0)
        rw.setSpacing(8)
        rw.addLayout(self._labeled_combo("环结构",
            ["3n次分圆多项式环", "2n次分圆多项式环"],
            "ring_combobox",
            layout_only=True))
        self.ring_widget.hide()
        layout.addWidget(self.ring_widget)

        add_shadow(card)
        self.main.addWidget(card)

    def _labeled_combo(self, title, items, attr_name, layout_only=False):
        """创建 '标题 + 下拉框' 的垂直组合，并把下拉框注册为 self.<attr_name>。"""
        col = QVBoxLayout()
        col.setSpacing(8)
        col.addWidget(SectionTitle(title))
        cb = QComboBox()
        cb.addItems(items)
        cb.setFont(FONT_BODY)
        cb.setFixedHeight(50)
        cb.setStyleSheet(COMBO_STYLE)
        col.addWidget(cb)
        setattr(self, attr_name, cb)
        return col

    def _build_params_card(self):
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        # 标题行
        header_row = QHBoxLayout()
        header_row.addWidget(SectionTitle("输入参数"))
        header_row.addStretch()
        self.param_count = StatusBadge()
        header_row.addWidget(self.param_count)
        layout.addLayout(header_row)
        layout.addWidget(Divider())

        # 参数网格
        self.param_labels = {}
        self.param_inputs = {}
        self.input_layout = QGridLayout()
        self.input_layout.setHorizontalSpacing(18)
        self.input_layout.setVerticalSpacing(14)
        layout.addLayout(self.input_layout)

        add_shadow(card)
        self.main.addWidget(card)

    def _build_button(self):
        row = QHBoxLayout()
        row.addStretch()
        self.calculate_button = QPushButton("开始评估")
        self.calculate_button.setFixedSize(230, 56)
        self.calculate_button.setFont(FONT_BOLD)
        self.calculate_button.setCursor(Qt.PointingHandCursor)
        self.calculate_button.setStyleSheet(BUTTON_STYLE)
        add_shadow(self.calculate_button, r=20, c="#93C5FD", dy=5)
        row.addWidget(self.calculate_button)
        row.addStretch()
        self.main.addLayout(row)

    def _build_result_card(self):
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        header_row = QHBoxLayout()
        header_row.addWidget(SectionTitle("评估结果"))
        header_row.addStretch()
        self.status_badge = StatusBadge()
        header_row.addWidget(self.status_badge)
        layout.addLayout(header_row)
        layout.addWidget(Divider())

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setMinimumHeight(260)
        self.result_box.setFont(FONT_MONO)
        self.result_box.setPlaceholderText("评估结果将在此处显示……")
        self.result_box.setStyleSheet(RESULT_STYLE)
        layout.addWidget(self.result_box)

        add_shadow(card)
        self.main.addWidget(card)

    # ── 逻辑 ──────────────────────────────────────────────────────

    def _real_alg(self):
        alg = self.algorithm_combobox.currentText()
        if alg in ["MLWE", "RLWE"]:
            ring = self.ring_combobox.currentText()
            return f"{alg}_{'3n' if '3n' in ring else '2n'}"
        return alg

    def update_params(self):
        alg = self.algorithm_combobox.currentText()
        self.ring_widget.setVisible(alg in ["MLWE", "RLWE"])

        # 清空旧参数控件
        for w in list(self.param_labels.values()) + list(self.param_inputs.values()):
            w.deleteLater()
        self.param_labels.clear()
        self.param_inputs.clear()

        params = get_algorithm_params(self._real_alg(), self.eval_type_combobox.currentText())

        for idx, param in enumerate(params):
            grid_row = idx % 5
            grid_col = (idx // 5) * 2

            lbl = QLabel(param)
            lbl.setFont(FONT_SUB)
            lbl.setStyleSheet(f"color: {TEXT_SUB};")
            self.input_layout.addWidget(lbl, grid_row, grid_col)

            inp = QLineEdit()
            inp.setFont(FONT_BODY)
            inp.setFixedHeight(46)
            inp.setPlaceholderText("请输入")
            inp.setStyleSheet(INPUT_STYLE)
            self.input_layout.addWidget(inp, grid_row, grid_col + 1)

            self.param_labels[param] = lbl
            self.param_inputs[param] = inp

        self.param_count.setText(f"  {len(params)} 个参数  ")
        self.param_count.set_ready()
        self.result_box.clear()
        self.status_badge.set_ready()

    def on_calculate_click(self):
        self.status_badge.set_running()
        self.result_box.setText("正在计算，请稍候……")
        self.calculate_button.setEnabled(False)
        QTimer.singleShot(60, self._do_evaluate)

    def _do_evaluate(self):
        real_alg  = self._real_alg()
        eval_type = self.eval_type_combobox.currentText()
        params    = get_algorithm_params(real_alg, eval_type)
        values    = [self.param_inputs[p].text().strip() for p in params]

        result = evaluate_performance(real_alg, values, eval_type)
        self.result_box.setText(result)
        self.status_badge.set_done()
        self.calculate_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = CryptoEvaluator()
    window.show()
    sys.exit(app.exec_())