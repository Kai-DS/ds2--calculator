import flet as ft
import math

class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text

class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.colors.WHITE24
        self.color = ft.colors.WHITE

class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.ORANGE
        self.color = ft.colors.WHITE

class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.BLUE_GREY_100
        self.color = ft.colors.BLACK

class ScientificButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.GREEN_200
        self.color = ft.colors.BLACK

class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.colors.WHITE, size=20)
        self.width = 400  # 少し幅を広げて科学的関数のボタンを追加
        self.bgcolor = ft.colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                # 科学的関数のための新しい行を追加
                ft.Row(
                    controls=[
                        ScientificButton(text="sin", button_clicked=self.button_clicked),
                        ScientificButton(text="cos", button_clicked=self.button_clicked),
                        ScientificButton(text="tan", button_clicked=self.button_clicked),
                        ScientificButton(text="√", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ScientificButton(text="log", button_clicked=self.button_clicked),
                        ScientificButton(text="ln", button_clicked=self.button_clicked),
                        ScientificButton(text="^", button_clicked=self.button_clicked),
                        ScientificButton(text="π", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(
                            text="AC", button_clicked=self.button_clicked
                        ),
                        ExtraActionButton(
                            text="+/-", button_clicked=self.button_clicked
                        ),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(
                            text="0", expand=2, button_clicked=self.button_clicked
                        ),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        
        # エラー状態またはACボタンの場合はリセット
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()

        # 数字と小数点の入力処理
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        # 基本的な演算子の処理
        elif data in ("+", "-", "*", "/"):
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True

        # 科学的関数の処理
        elif data in ("sin", "cos", "tan"):
            try:
                # ラジアンに変換
                value = float(self.result.value)
                if data == "sin":
                    self.result.value = str(math.sin(math.radians(value)))
                elif data == "cos":
                    self.result.value = str(math.cos(math.radians(value)))
                else:  # tan
                    self.result.value = str(math.tan(math.radians(value)))
            except Exception:
                self.result.value = "Error"

        # 平方根
        elif data == "√":
            try:
                value = float(self.result.value)
                if value < 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(math.sqrt(value))
            except Exception:
                self.result.value = "Error"

        # 対数関数
        elif data == "log":
            try:
                value = float(self.result.value)
                if value <= 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(math.log10(value))
            except Exception:
                self.result.value = "Error"

        # 自然対数
        elif data == "ln":
            try:
                value = float(self.result.value)
                if value <= 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(math.log(value))
            except Exception:
                self.result.value = "Error"

        # べき乗
        elif data == "^":
            self.operator = "^"
            self.operand1 = float(self.result.value)
            self.new_operand = True

        # 円周率
        elif data == "π":
            self.result.value = str(math.pi)

        # イコールボタン
        elif data == "=":
            if self.operator == "^":
                try:
                    self.result.value = str(self.operand1 ** float(self.result.value))
                except Exception:
                    self.result.value = "Error"
            else:
                self.result.value = self.calculate(
                    self.operand1, float(self.result.value), self.operator
                )
            self.reset()

        # パーセンテージと符号変更の処理は以前と同じ
        elif data == "%":
            self.result.value = float(self.result.value) / 100
            self.reset()

        elif data == "+/-":
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)
            elif float(self.result.value) < 0:
                self.result.value = str(
                    self.format_number(abs(float(self.result.value)))
                )

        self.update()

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):
        if operator == "+":
            return self.format_number(operand1 + operand2)
        elif operator == "-":
            return self.format_number(operand1 - operand2)
        elif operator == "*":
            return self.format_number(operand1 * operand2)
        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True

def main(page: ft.Page):
    page.title = "Scientific Calc App"
    calc = CalculatorApp()
    page.add(calc)
    

ft.app(target=main)