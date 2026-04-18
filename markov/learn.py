"""
learn.py — 学習モジュール

markov.learn.add(url) でURLからテキストを学習し、
markov.learn.reset でデータをリセットする。
"""

from . import core as _core_module


class AddDispatcher:
    """
    () で呼び出された場合は URL 学習、
    [] で呼び出された場合はファイル学習を行うディスパッチャ。
    """

    def __init__(self, core: '_core_module.MarkovCore'):
        self._core = core

    def __call__(self, url: str) -> None:
        """markov.learn.add("URL") の形式で呼び出された際に実行。"""
        if not isinstance(url, str):
            raise TypeError(f"URLは文字列で指定してください。受け取った型: {type(url).__name__}")
        self._core.learn_url(url.strip())

    def __getitem__(self, path: str) -> None:
        """markov.learn.add["PATH"] の形式で呼び出された際に実行。"""
        if not isinstance(path, str):
            raise TypeError(f"パスは文字列で指定してください。受け取った型: {type(path).__name__}")
        self._core.learn_file(path.strip())


class LearnModule:
    """
    マルコフ連鎖の学習を管理するモジュール。

    使い方:
        markov.learn.add("https://example.com")  # URL学習
        markov.learn.add["~/markov.txt"]         # ファイル学習
        markov.learn.reset
    """

    def __init__(self, core: '_core_module.MarkovCore'):
        # コアエンジンへの参照
        self._core = core
        # 特殊な API を提供するためのディスパッチャ
        self.add = AddDispatcher(core)

    @property
    def reset(self) -> None:
        """
        学習データをリセットする。括弧なしで呼び出す。
        """
        self._core.reset()
