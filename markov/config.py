"""
config.py — 設定モジュール

markov.config.max / markov.config.min で文章生成の最大・最小単語数を設定する。
"""


class ConfigModule:
    """
    文章生成の設定を管理するモジュール。

    使い方:
        markov.config.max = 150  # 最大単語数
        markov.config.min = 20   # 最小単語数
    """

    def __init__(self):
        # デフォルト値
        self._max: int = 100
        self._min: int = 10

    @property
    def max(self) -> int:
        """文章生成の最大単語数（デフォルト: 100）。"""
        return self._max

    @max.setter
    def max(self, value: int) -> None:
        if not isinstance(value, int) or value < 1:
            raise ValueError(f"max は1以上の整数で指定してください: {value}")
        if value < self._min:
            raise ValueError(f"max ({value}) は min ({self._min}) 以上にしてください")
        self._max = value

    @property
    def min(self) -> int:
        """文章生成の最小単語数（デフォルト: 10）。"""
        return self._min

    @min.setter
    def min(self, value: int) -> None:
        if not isinstance(value, int) or value < 1:
            raise ValueError(f"min は1以上の整数で指定してください: {value}")
        if value > self._max:
            raise ValueError(f"min ({value}) は max ({self._max}) 以下にしてください")
        self._min = value
