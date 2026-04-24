"""
learn.py — 学習モジュール

markov.learn.add("https://...")  → URLからテキストを学習
markov.learn.add["path/to/file"] → テキストファイルから直接学習
markov.learn.reset               → 学習データをリセット
"""

from . import core as _core_module


class _AddProxy:
    """
    add を関数呼び出し（丸括弧）と添字アクセス（角括弧）の両方に対応させるクラス。

    markov.learn.add("https://...")     → URL学習
    markov.learn.add["path/to/file"]    → ファイル学習
    """

    def __init__(self, core: '_core_module.MarkovCore'):
        # コアエンジンへの参照
        self._core = core

    def __call__(self, url: str) -> None:
        """
        URLからテキストを学習する（丸括弧で呼び出す）。

        Args:
            url (str): 学習対象のURL（http / https）

        Raises:
            ValueError: URLが無効・取得できない場合
            TypeError: url が文字列でない場合
        """
        if not isinstance(url, str):
            raise TypeError(f"URLは文字列で指定してください。受け取った型: {type(url).__name__}")
        self._core.learn_url(url.strip())

    def __getitem__(self, path: str) -> None:
        """
        テキストファイルから直接学習する（角括弧で呼び出す）。

        使い方:
            markov.learn.add["sample.txt"]
            markov.learn.add["~/documents/text.txt"]
            markov.learn.add["/home/user/text.txt"]

        Args:
            path (str): テキストファイルのパス（相対・絶対・~ 表記すべて可）

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            ValueError: ファイルを読み込めない場合
            TypeError: path が文字列でない場合
        """
        if not isinstance(path, str):
            raise TypeError(f"パスは文字列で指定してください。受け取った型: {type(path).__name__}")
        self._core.learn_file(path.strip())


class LearnModule:
    """
    マルコフ連鎖の学習を管理するモジュール。

    使い方:
        markov.learn.add("https://example.com")   # URL学習
        markov.learn.add["sample.txt"]             # ファイル学習
        markov.learn.reset                         # リセット
    """

    def __init__(self, core: '_core_module.MarkovCore'):
        # コアエンジンへの参照
        self._core = core
        # add は URL（丸括弧）でもファイル（角括弧）でも使えるプロキシ
        self.add = _AddProxy(core)

    @property
    def reset(self) -> None:
        """
        学習データをリセットする。括弧なしで呼び出す。

        使い方:
            markov.learn.reset
        """
        self._core.reset()
