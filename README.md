# markov-learning

言語レベルでのマルコフ連鎖を簡単に体験できるPythonライブラリです。
URLを指定するだけでWebページのテキストを学習し、マルコフ連鎖による文章を生成します。

日本語、JavaScriptのWebページに対応しており、同じ階層のみを学習します。

---

## インストール

```bash
pip install git+https://github.com/AtsukiY/markov.git
```

JavaScriptを利用しているWebページから学習する場合、初回実行時に
別ライブラリがダウンロードされるため、処理に時間がかかります。

---

## 使い方

```python
import markov

# URLからテキストを学習する
markov.learn.add("https://example.com")
markov.learn.add("https://example.com/example")

## 変数にURLを入れて渡すことも可能
url = "https://example.com"
markov.learn.add(url)

# テキストファイルからテキストを学習する
markov.learn.add["~/markov.txt"]

## 変数にpathを入れて渡すことも可能
path = "~/markov"
markov.learn.add[path]

# 文章を生成する
print(markov.output)

## 変数に代入することも可能
x = markov.output
print(x)

# 学習データをリセットする
markov.learn.reset

# 設定変更
## 最大単語数 デフォルト：100
markov.config.max = 150
## 最小単語数 デフォルト：10
markov.config.min = 20
```

---

## エラーについて

```python
# 無効なURLを指定するとエラーが発生します
markov.learn.add("https://invalid.example.invalid")
# → ValueError: URLに接続できません: https://invalid.example.invalid

# URLが文字列でない場合もエラーになります
markov.learn.add(12345)
# → TypeError: URLは文字列で指定してください。受け取った型: int
```

---

## アップデート履歴

### 1.0.0
- URLからのテキスト学習に対応させました。
- マルコフ連鎖による文章生成をできるようにしました。
- 学習データリセットをできるようにしました。
- 日本語を対応させました。
- JavaScriptサイト対応させました。
- 繰り返しループ抑制機能を搭載しました。
- 最大・最小単語数の設定できるようにしました。

### 1.1.0
- テキストファイルからのテキスト学習に対応させました。
- JavaScriptサイトからの学習に必要なライブラリを自動インストールするようにしました。
 
---

## 作者

Atsuki.Y
