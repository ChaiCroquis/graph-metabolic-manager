# CLAUDE.md — プロジェクト固有のAI作業ルール

このファイルはClaude Codeが毎セッション開始時に自動で読み込むルールです。

---

## プロジェクト概要

- **特許**: 特願2026-027032（請求項50項）
- **ライセンス**: Apache 2.0 + 特許除外条項
- **Python**: 3.10+、NumPy依存
- **テストフレームワーク**: pytest
- **リンター**: ruff（line-length=99、E501は無視）
- **型チェック**: mypy（disallow_untyped_defs=true）
- **Windows環境**: cp932エンコーディング制約あり（ログにUnicode数学記号禁止）
- **乱数シード**: 再現性のため常に `random.seed(42)` と `np.random.seed(42)` をセットで使用

---

## 必須ルール: 作業中の整合性チェック（後回し禁止）

### コードを書いたとき

- [ ] 関連ドキュメント（README, CHANGELOG, docs/）の数値・記述と突合する
- [ ] `__init__.py` の `__all__` に公開すべきシンボルを**同時に**追加する
- [ ] 既存モジュールで確立されたパターン（下記「コード規約」参照）を新コードにも統一適用する
- [ ] マジックナンバーは即座に `DEFAULT_` または `_` 接頭辞の名前付き定数にする
- [ ] 全関数に型アノテーションを付ける（mypy strict設定）

### ドキュメント・論文を書いたとき

- [ ] 記載した数式が実際のコードの実装と一致するか、該当ソースファイルを開いて確認する
- [ ] シリーズ記事の場合、前回/次回リンクを全記事で統一的に設置する
- [ ] テスト数・ファイル数などの数値は `pytest --co -q` やファイル一覧で実数を確認する
- [ ] テーブルの行数が見出しの件数と一致するか数える

### ライセンス・バージョンを変えたとき

- [ ] `grep -r` で旧表記の残留を全ファイル検索する（.egg-info, .mypy_cache除外）
- [ ] 以下4箇所を同時に更新する:
  - `pyproject.toml` (version)
  - `__init__.py` (__version__)
  - `CHANGELOG.md` (新エントリ)
  - `CLAUDE.md` (「現在の状態」セクション)

### テスト数が変わったとき

以下の全箇所を同時に更新する:
- `README.md` (バッジ付近、Verification テーブル)
- `CHANGELOG.md`
- `CLAUDE.md` (「現在の状態」セクション)
- `docs/verification_report.md` (英語・日本語両方)
- `docs/paper-series/06_検証編.md`

### 全般

- **「後でまとめて検証」は禁止**。各ステップの完了時にそのステップに関連する整合性を確認する
- テスト実行 (`pytest`) とリント (`ruff check`) は変更の都度実行する

---

## コード規約

### モジュール docstring

```python
"""
ModuleName — Brief description.

Detailed description of what the module does.

Patent claims: N-M
Key formula: formula_here
"""
```

- em-dash（`—`）を使用、`--` ではない
- 特許対応の請求項範囲を必ず記載

### import 順序

```python
from __future__ import annotations          # 1. 常に最初

import logging                               # 2. 標準ライブラリ
import math
from typing import TYPE_CHECKING

import numpy as np                           # 3. サードパーティ

from ._logging import TRACE                  # 4. ローカル

if TYPE_CHECKING:                            # 5. 型チェック専用（循環import回避）
    from .graph import Graph
```

- `from __future__ import annotations` は**全モジュール必須**（PEP 604対応）
- `Graph` は `TYPE_CHECKING` ブロック内でのみ import（循環依存回避）

### DEFAULT_ 定数パターン

```python
# ------------------------------------------------------------------
# Default parameters (Patent specification, Fig. 13B)
# ------------------------------------------------------------------
DEFAULT_ALPHA = 2.0      # Congestion sensitivity exponent
```

- セクション区切り: `# ` + `-` × 66
- 公開定数: `DEFAULT_<UPPER_NAME>`
- 非公開定数: `_<UPPER_NAME>`（例: `_EMA_RETAIN`）
- インラインコメントでパラメータの意味を説明

### パラメータ検証パターン

```python
if alpha <= 0:
    raise ValueError(f"alpha must be positive, got {alpha}")
```

- `__init__` の冒頭で、代入前に検証
- メッセージ形式: `f"{param} must be {constraint}, got {value}"`

### TRACE ログ形式

```python
if logger.isEnabledFor(TRACE):
    logger.log(TRACE, "module_prefix: context key=value, ...")
```

- 必ず `if logger.isEnabledFor(TRACE):` でガード
- モジュール接頭辞: `metabolic:`, `rarity:`, `consistency:`, `meta:`, `manager:`
- アクション語は大文字: `SKIP`, `ENTER`, `REMOVE`, `RELEASE`, `ACCEPT`, `REJECT`, `PRUNE`
- ステップ境界: `"manager: === step t=%d begin ==="`, `"manager: === step t=%d end ==="`
- **Unicode数学記号禁止**（cp932制約）— `lambda`→`lam`, `alpha`→`alpha` 等ASCII表記

### ロガー宣言

```python
logger = logging.getLogger(__name__)
```

- import直後、`TYPE_CHECKING` ブロック前に配置
- 変数名は常に `logger`（小文字・単数）

---

## テスト規約

### テストクラス

```python
class TestComponentName:
    """ComponentName: brief description of what is tested."""
```

### テストファイル

```python
"""Tests for ComponentName: brief description."""
```

- ファイル名: `test_<component>.py`

### 特許検証テスト構造

- `_build_standard()` でグラフ生成 → `(graph, normal_ids, rare_ids, garbage_ids)` 返却
- `SCENARIOS` dict にシナリオ名→ビルダー関数をマッピング
- `@pytest.mark.parametrize` で28業界を横断テスト
- 5カテゴリ × 28業界 = 560テスト

### アサーション

- float比較には `pytest.approx()` を使用
- parametrize テストでは `f"[{name}] description"` 形式のメッセージ

---

## アーキテクチャ

### モジュール依存関係

```
_logging.py     ← 依存なし（TRACE定数のみ）
graph.py        ← 依存なし（データ構造のみ）
metabolic.py    ← _logging, graph(TYPE_CHECKING)
rarity.py       ← _logging, graph(TYPE_CHECKING)
consistency.py  ← _logging, graph(TYPE_CHECKING), numpy
meta_control.py ← _logging, graph(TYPE_CHECKING)
manager.py      ← 全モジュール（ファサード/オーケストレーター）
__init__.py     ← 全モジュール（公開API再エクスポート）
```

- `metabolic`, `rarity`, `consistency`, `meta_control` の4モジュールは相互に依存しない
- `manager.py` のみが全モジュールをランタイムで import
- `Graph` は TYPE_CHECKING で型のみ import（循環防止）

### ファイル命名

- `_logging.py`, `_runner.py`: アンダースコア接頭辞 = 内部実装、直接importしない
- `examples/NN_name.py`: 01-06は独立スクリプト、07-28は `_runner.py` 経由
- `docs/paper-series/NN_name.md`: 日本語のみ（Qiita/Zenn向け）

### 特許請求項とモジュールの対応

| モジュール | 請求項 |
|---|---|
| metabolic.py | 1-10 |
| rarity.py | 11-20 |
| consistency.py | 21-26 |
| meta_control.py | 27-32 |
| manager.py (階層管理) | 20-26 |
| 組合せ | 33-50 |

---

## ドキュメント規約

### 言語方針

| ファイル | 言語 |
|---|---|
| README.md | 英語先、末尾に日本語 |
| PATENT_NOTICE.md | 英語先、末尾に日本語 |
| CHANGELOG.md | 英語のみ |
| docs/verification_report.md | 英語先、末尾に日本語 |
| docs/paper-series/*.md | 日本語のみ |
| CLAUDE.md | 日本語 |

### CHANGELOG エントリ形式

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- **Feature name** (`file.py`) — Description
```

- 機能名を太字、ファイル名をバッククォート、em-dashで説明

---

## ビルド・テストコマンド

```bash
# テスト実行（Windows）
C:/Users/user/AppData/Local/Programs/Python/Python313/python.exe -m pytest C:/work/graph-metabolic-manager/tests/ -q

# リント
C:/Users/user/AppData/Local/Programs/Python/Python313/python.exe -m ruff check C:/work/graph-metabolic-manager/graph_metabolic_manager/ C:/work/graph-metabolic-manager/tests/

# TRACEログ確認
C:/Users/user/AppData/Local/Programs/Python/Python313/python.exe -c "import logging; from graph_metabolic_manager import *; logging.basicConfig(level=TRACE)"
```

---

## 既知のプレースホルダ（ユーザーが手動対応）

- GitHubユーザー名: `ChaiCroquis`（置換済み）
- メールアドレス: `garden.of.knowledge.chai@gmail.com`（置換済み）

---

## 現在の状態

- **バージョン**: 0.2.1
- **テスト**: 629件全パス（コア69 + 特許検証560）
- **ruff**: クリーン
- **公開シンボル数**: 16（`__all__` に定義）
