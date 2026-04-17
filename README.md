# markov-learning

言語レベルでのマルコフ連鎖を簡単に体験できるPythonライブラリです。  
URLを指定するだけでWebページのテキストを学習し、マルコフ連鎖による文章を生成します。

- **日本語対応**: janome による形態素解析で高精度な日本語学習
- **JavaScript対応**: playwright により、Twitter/X・YouTubeなどのJSサイトにも対応
- **階層制限**: 同じ階層のリンクのみを学習対象とし、膨大なデータの取り込みを防止

---

## インストール

```bash
pip install markov-learning
```

JavaScriptで構成されたサイト（Twitter/X、YouTubeなど）から学習する場合は、
初回のみ以下のコマンドでブラウザのインストールが必要です。

```bash
playwright install chromium
```

---

## 使い方

```python
import markov

# URLからテキストを学習する（同じ階層のリンクのみ対象）
markov.learn.add("https://www.asahi.com/")
markov.learn.add("https://en.wikipedia.org/wiki/Markov_chain")

# 変数にURLを入れて渡すことも可能
url = "https://example.com"
markov.learn.add(url)

# 文章を生成する（括弧なし）
print(markov.output)

# 変数に代入することも可能
x = markov.output
print(x)

# 学習データをリセットする（括弧なし）
markov.learn.reset

# 設定変更（任意）
markov.config.max = 150  # 最大単語数（デフォルト: 100）
markov.config.min = 20   # 最小単語数（デフォルト: 10）
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
- 初回リリース
- URLからのテキスト学習（`markov.learn.add`）
- マルコフ連鎖による文章生成（`markov.output`）
- 学習データリセット（`markov.learn.reset`）
- 日本語形態素解析（janome）対応
- JavaScriptサイト対応（playwright）
- 繰り返しループ抑制機能
- 最大・最小単語数の設定（`markov.config`）

---

## 作者

Atsuki.Y
