"""
core.py — マルコフ連鎖エンジン

テキストの学習・文章生成を担うコアモジュール。
日本語テキストは janome で形態素解析し、英語テキストは単語分割で処理する。
JavaScriptで構成されたサイトは playwright によるフォールバックで対応する。
"""

import random
import re
from collections import defaultdict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# janome（日本語形態素解析）が利用可能かを確認
try:
    from janome.tokenizer import Tokenizer as JanomeTokenizer
    _JANOME_AVAILABLE = True
except ImportError:
    _JANOME_AVAILABLE = False

# playwright が利用可能かを確認
try:
    from playwright.sync_api import sync_playwright
    _PLAYWRIGHT_AVAILABLE = True
except ImportError:
    _PLAYWRIGHT_AVAILABLE = False

# ---- 定数 ----------------------------------------------------------------

# JSレンダリングが必要と判断するための <script> タグ数の閾値
_JS_THRESHOLD = 5

# 取得タイムアウト（秒）
_REQUEST_TIMEOUT = 15

# ---- 内部ユーティリティ --------------------------------------------------

def _is_japanese(text: str) -> bool:
    """テキストに日本語文字が含まれているか判定する。"""
    return bool(re.search(r'[\u3040-\u9fff]', text))


def _tokenize(text: str) -> list[str]:
    """
    テキストをトークン（単語）のリストに変換する。
    日本語は janome で形態素解析、英語は空白・句読点で分割する。
    """
    if _is_japanese(text):
        if _JANOME_AVAILABLE:
            tokenizer = JanomeTokenizer()
            tokens = []
            for token in tokenizer.tokenize(text):
                surface = token.surface
                # 空白・改行・記号を除外
                if surface.strip() and surface not in ('　', '\n', '\r'):
                    tokens.append(surface)
            return tokens
        else:
            # janome が無い場合は文字単位に分割（精度は低下）
            return list(text.replace(' ', '').replace('\n', ''))
    else:
        # 英語：単語単位で分割（句読点は区切り文字として扱う）
        tokens = re.findall(r"[a-zA-Z']+|[.!?。、]", text)
        return [t for t in tokens if t.strip()]


def _fetch_html_simple(url: str) -> str:
    """
    requests + BeautifulSoup でHTMLを取得する。
    取得失敗時は ValueError を raise する。
    """
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept-Language': 'ja,en;q=0.9',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=_REQUEST_TIMEOUT)
    except requests.exceptions.ConnectionError:
        raise ValueError(f"URLに接続できません: {url}")
    except requests.exceptions.Timeout:
        raise ValueError(f"接続がタイムアウトしました: {url}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"URLの取得中にエラーが発生しました: {url} ({e})")

    if resp.status_code >= 400:
        raise ValueError(
            f"URLが無効または取得できません (HTTP {resp.status_code}): {url}"
        )

    # 文字コードの自動検出（Content-Type の charset を優先し、不明なら apparent_encoding を使用）
    if resp.encoding is None or resp.encoding.lower() in ('iso-8859-1', 'windows-1252'):
        resp.encoding = resp.apparent_encoding

    return resp.text


def _fetch_html_playwright(url: str) -> str:
    """
    playwright でブラウザを起動し、JavaScriptをレンダリングしてHTMLを取得する。
    playwright / Chromium が未インストールの場合は ValueError を raise する。
    """
    if not _PLAYWRIGHT_AVAILABLE:
        raise ValueError(
            "playwright がインストールされていません。"
            "`pip install playwright` の後に `playwright install chromium` を実行してください。"
        )
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until='domcontentloaded')
            # 動的コンテンツが読み込まれるまで少し待機
            page.wait_for_timeout(2000)
            html = page.content()
            browser.close()
        return html
    except Exception as e:
        raise ValueError(f"playwright によるページ取得に失敗しました: {url} ({e})")


def _needs_js(html: str) -> bool:
    """ページが JS レンダリングを必要とするか簡易判定する。"""
    soup = BeautifulSoup(html, 'lxml')
    scripts = soup.find_all('script')
    text = soup.get_text(separator=' ', strip=True)
    # スクリプト数が多く、かつ本文テキストが少ない場合に JS 必要と判断
    return len(scripts) >= _JS_THRESHOLD and len(text) < 200


def _extract_text(html: str) -> str:
    """BeautifulSoup でHTMLから本文テキストを抽出する。"""
    soup = BeautifulSoup(html, 'lxml')
    # script / style タグを除去
    for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav']):
        tag.decompose()
    return soup.get_text(separator=' ', strip=True)


def _get_same_level_links(base_url: str, html: str) -> list[str]:
    """
    同じ階層のリンクのみを抽出して返す。
    例: https://example.com/news/ の場合、https://example.com/news/xxx のみ対象。
    """
    parsed = urlparse(base_url)
    # ベースパスの最初のセグメントまでを「同じ階層」とする
    # 例: /wiki/Markov_chain → /wiki/ が同階層プレフィックス
    path_parts = [p for p in parsed.path.split('/') if p]
    if path_parts:
        base_prefix = '/' + path_parts[0] + '/'
    else:
        base_prefix = '/'

    base_origin = f"{parsed.scheme}://{parsed.netloc}"
    soup = BeautifulSoup(html, 'lxml')
    links = set()

    for a in soup.find_all('a', href=True):
        href = a['href']
        # 絶対URLに変換
        full_url = urljoin(base_url, href)
        fp = urlparse(full_url)
        # 同じドメインかつ同じ階層プレフィックスのみ対象
        if fp.netloc == parsed.netloc and fp.path.startswith(base_prefix):
            # クエリ・フラグメントを除いたURLを追加
            clean = f"{fp.scheme}://{fp.netloc}{fp.path}"
            if clean != base_url:
                links.add(clean)

    return list(links)


# ---- MarkovCore ----------------------------------------------------------

class MarkovCore:
    """
    マルコフ連鎖の学習・文章生成を行うコアクラス。

    Attributes:
        chain (dict): word → [next_word, ...] のマッピング
        config: ConfigModule への参照（min/max 設定に使用）
    """

    def __init__(self):
        # {word: [next_word, ...]} 形式の連鎖データ
        self.chain: dict[str, list[str]] = defaultdict(list)
        # ConfigModule は __init__.py から後から設定される
        self.config = None

    # ---- 学習 ------------------------------------------------------------

    def learn_url(self, url: str) -> None:
        """
        指定URLのテキストをマルコフ連鎖として学習する。
        URLが無効・取得できない場合は ValueError を raise する。
        """
        # URLの形式チェック
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            raise ValueError(f"有効なURL（http/https）を指定してください: {url}")

        # まず通常取得を試みる
        html = _fetch_html_simple(url)

        # JSレンダリングが必要と判断した場合は playwright でリトライ
        if _needs_js(html):
            try:
                html = _fetch_html_playwright(url)
            except ValueError:
                # playwright が使えない場合は通常取得結果をそのまま使う
                pass

        text = _extract_text(html)
        self._learn_text(text)

    def _learn_text(self, text: str) -> None:
        """テキストをトークナイズしてマルコフ連鎖に追加する。"""
        tokens = _tokenize(text)
        if len(tokens) < 2:
            return
        for i in range(len(tokens) - 1):
            self.chain[tokens[i]].append(tokens[i + 1])

    def reset(self) -> None:
        """学習データをリセットする。"""
        self.chain = defaultdict(list)

    # ---- 生成 ------------------------------------------------------------

    def generate(self) -> str:
        """
        学習済みのマルコフ連鎖から文章を生成して返す。
        学習データが無い場合は空文字列を返す。
        """
        if not self.chain:
            return ""

        # min/max の取得（config が設定されていない場合はデフォルト値を使用）
        max_words = self.config.max if self.config else 100
        min_words = self.config.min if self.config else 10

        result = []
        # 文頭になりやすい単語（大文字始まりか、日本語の短い単語）を優先的に選択
        start_candidates = [
            w for w in self.chain
            if (w and w[0].isupper()) or (len(w) <= 3 and _is_japanese(w))
        ]
        current = random.choice(start_candidates if start_candidates else list(self.chain.keys()))

        # 繰り返し抑制用の直近単語バッファ
        recent: list[str] = []

        for _ in range(max_words):
            result.append(current)
            recent.append(current)
            # 直近5単語で同じ単語が3回以上出た場合はループと判断してスキップ
            if len(recent) > 5:
                recent.pop(0)
            if recent.count(current) >= 3:
                # ループを避けるためランダムな別の単語に飛ぶ
                current = random.choice(list(self.chain.keys()))
                continue

            nexts = self.chain.get(current)
            if not nexts:
                # 次の単語がない → 文末
                if len(result) >= min_words:
                    break
                # min に満たない場合はランダムな単語から継続
                current = random.choice(list(self.chain.keys()))
                continue

            # 句読点による文末判定
            next_word = random.choice(nexts)
            if next_word in ('。', '.', '!', '?', '！', '？') and len(result) >= min_words:
                result.append(next_word)
                break

            current = next_word

        return ''.join(result) if _is_japanese(''.join(result)) else ' '.join(result)


# ---- シングルトンインスタンス --------------------------------------------

# markov パッケージ全体で共有するコアインスタンス
_core = MarkovCore()
