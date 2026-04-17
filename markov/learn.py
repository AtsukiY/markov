"""
learn.py — 学習モジュール

markov.learn.add(url) でURLからテキストを学習し、
markov.learn.reset でデータをリセットする。
"""

from . import core as _core_module


class LearnModule:
    """
    マルコフ連鎖の学習を管理するモジュール。

    使い方:
        markov.learn.add("https://example.com")
        markov.learn.reset
    """

    def __init__(self, core: '_core_module.MarkovCore'):
        # コアエンジンへの参照
        self._core = core

    def add(self, url: str) -> None:
        """
        指定URLのページを学習する。同じ階層のリンクのみを対象とする。

        Args:
            url (str): 学習対象のURL（http / https）

        Raises:
            ValueError: URLが無効・取得できない場合
            TypeError: url が文字列でない場合
        """
        if not isinstance(url, str):
            raise TypeError(f"URLは文字列で指定してください。受け取った型: {type(url).__name__}")

        # 先頭・末尾の空白を除去
        url = url.strip()
        self._core.learn_url(url)

    @property
    def reset(self) -> None:
        """
        学習データをリセットする。括弧なしで呼び出す。

        使い方:
            markov.learn.reset
        """
        self._core.reset()
