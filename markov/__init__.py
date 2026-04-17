"""
markov — 言語レベルのマルコフ連鎖ライブラリ

使い方:
    import markov

    # URLからテキストを学習する
    markov.learn.add("https://example.com")

    # 文章を生成する
    print(markov.output)
    x = markov.output

    # 学習データをリセットする
    markov.learn.reset

    # 設定変更（任意）
    markov.config.max = 150
    markov.config.min = 20
"""

from .core import _core
from .learn import LearnModule
from .config import ConfigModule

# ---- 設定モジュールをコアに接続 -----------------------------------------
config = ConfigModule()
_core.config = config

# ---- 学習モジュール ------------------------------------------------------
learn = LearnModule(_core)


# ---- パブリックAPI -------------------------------------------------------

class _MarkovModule:
    """
    markov パッケージのトップレベルAPI。
    output プロパティで文章を生成する。
    """

    def __init__(self):
        self.learn = learn
        self.config = config

    @property
    def output(self) -> str:
        """
        学習データからマルコフ連鎖で文章を生成して返す。
        括弧なしで呼び出す。

        使い方:
            print(markov.output)
            x = markov.output
        """
        return _core.generate()


# モジュール自体を _MarkovModule インスタンスで置き換える
import sys as _sys

class _MarkovPackage(_MarkovModule):
    """sys.modules に登録してモジュールレベルのプロパティを有効にするクラス。"""

    # モジュールとしての属性をそのまま引き継ぐ
    __name__     = __name__
    __loader__   = __loader__   # noqa: F821
    __spec__     = __spec__     # noqa: F821
    __package__  = __package__  # noqa: F821
    __path__     = __path__     # noqa: F821
    __file__     = __file__


# モジュールオブジェクト自体を差し替えて `markov.output` をプロパティとして動作させる
_sys.modules[__name__] = _MarkovPackage()
