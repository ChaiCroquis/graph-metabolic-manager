# Patent Notice / 特許に関するお知らせ

## English

### Patent Information

This repository contains a reference implementation of algorithms described in the following patent application:

- **Application Number**: Japanese Patent Application No. 2026-027032
- **Title**: Data Structure Management System Using Rarity Protection and Consistency Discovery
  (希少性保護及び整合性発見を用いたデータ構造管理システム、情報処理方法及びプログラム)
- **IPC Classification**: G06F 16/21, G06F 16/906
- **Filing Date**: February 24, 2026
- **Inventor**: Yasuhiro Kuroki
- **Status**: Patent Pending (出願中)
- **Number of Claims**: 50 (48 system + 1 method + 1 program)

### Licensing Structure

This project uses a **dual licensing** model:

| Aspect | License | Details |
|---|---|---|
| **Source code** (copyright) | Apache License 2.0 | Free to use, modify, and redistribute |
| **Patented algorithms** (patent rights) | Separate patent license required for commercial use | See below |

The Apache License 2.0 Section 3 grants a patent license for contributions to the code. However, the **Patent Exclusion Notice** in the LICENSE file explicitly excludes the patented algorithms (Claims 1-50) from that grant. This means:

- You may freely use, modify, and distribute the **source code** under Apache 2.0
- **Commercial use of the patented algorithms** requires a separate patent license
- Non-commercial use of the algorithms is permitted without a patent license

### When is a Patent License Required?

| Use Case | Patent License |
|---|---|
| Reading and studying the source code | Not required |
| Academic research and publications | Not required |
| Non-commercial evaluation and testing | Not required |
| Internal proof of concept (PoC) | Not required |
| Modifying the code for non-commercial purposes | Not required |
| **Commercial product incorporating the algorithms** | **Required** |
| **Commercial service using the algorithms** | **Required** |
| **Resale or sublicensing of the algorithms** | **Required** |

### What Counts as "Commercial Use of the Algorithms"?

A patent license is required when the **patented methods** are used in a commercial context, regardless of whether this specific source code is used. The patented methods include:

1. Congestion-based adaptive edge weight decay (Claims 1-10)
2. Multi-phase rarity protection for isolated nodes (Claims 11-20)
3. Structural similarity discovery via Laplacian eigenvalue spectra (Claims 21-26)
4. Health-index-based meta control feedback loop (Claims 27-32)
5. Hierarchical layer management (Claims 20-26)
6. Combinations of the above (Claims 33-50)

### Available License Types

| License Type | Description |
|---|---|
| **Exclusive License** | Sole rights within a specified field/industry |
| **Non-Exclusive License** | Multiple licensees allowed |
| **Field-Limited License** | Rights limited to specific industry or use case |
| **Technical Support License** | License + implementation support |

### Contact for Licensing

For licensing inquiries, please contact:

- **Email**: [Your email address]
- **Subject line**: "Patent License Inquiry - 2026-027032"

Please include:
- Your company name and industry
- Intended use case
- Preferred license type

---

## 日本語

### 特許情報

本リポジトリは、以下の特許出願に記載されたアルゴリズムのリファレンス実装です。

- **出願番号**: 特願2026-027032
- **発明の名称**: 希少性保護及び整合性発見を用いたデータ構造管理システム、情報処理方法及びプログラム
- **国際特許分類**: G06F 16/21, G06F 16/906
- **出願日**: 令和8年（2026年）2月24日
- **発明者**: 黒木 康博
- **状態**: 出願中（特許権未確定）
- **請求項数**: 50項（システム48項 + 方法1項 + プログラム1項）

### ライセンス構造

本プロジェクトは**二重ライセンス**モデルを採用しています。

| 対象 | ライセンス | 詳細 |
|---|---|---|
| **ソースコード**（著作権） | Apache License 2.0 | 自由に利用・改変・再配布可能 |
| **特許アルゴリズム**（特許権） | 商用利用には別途特許ライセンスが必要 | 下記参照 |

Apache License 2.0の第3条は特許ライセンスを付与しますが、LICENSEファイル内の**特許除外条項**により、特許出願に記載されたアルゴリズム（請求項1-50）は除外されています。つまり:

- **ソースコード**はApache 2.0の下で自由に利用・改変・再配布できます
- **特許アルゴリズムの商用利用**には別途特許ライセンスが必要です
- アルゴリズムの非商用利用には特許ライセンスは不要です

### 特許ライセンスが必要なケース

| 利用目的 | 特許ライセンス |
|---|---|
| ソースコードの閲覧・学習 | 不要 |
| 学術研究・論文発表 | 不要 |
| 非商用の技術評価・テスト | 不要 |
| 社内PoC（概念実証） | 不要 |
| 非商用目的でのコード改変 | 不要 |
| **特許アルゴリズムを組み込んだ商用製品** | **必要** |
| **特許アルゴリズムを利用した商用サービス** | **必要** |
| **アルゴリズムの再販・サブライセンス** | **必要** |

### 「アルゴリズムの商用利用」とは

本ソースコードの使用の有無にかかわらず、**特許に記載された方法**を商用で利用する場合に特許ライセンスが必要です。特許に記載された方法とは:

1. 局所混雑度に基づくエッジ重みの適応的減衰（請求項1-10）
2. 孤立ノードの多段審査による希少性保護（請求項11-20）
3. ラプラシアン固有値スペクトルによる構造類似性発見（請求項21-26）
4. 健全性指標に基づくメタ制御フィードバックループ（請求項27-32）
5. 差分処理間隔を持つ階層管理（請求項20-26）
6. 上記の組合せ（請求項33-50）

### ライセンス形態

| 形態 | 概要 |
|---|---|
| **独占ライセンス** | 特定分野・業界において1社のみに利用許諾 |
| **非独占ライセンス** | 複数企業への並行的な利用許諾 |
| **分野限定ライセンス** | 特定の業界・用途に限定した許諾 |
| **技術協力付き** | ライセンスに加え実装支援を含む |

### お問い合わせ

ライセンスに関するお問い合わせ:

- **メール**: [メールアドレス]
- **件名**: 「特許ライセンスに関するお問い合わせ - 2026-027032」

以下の情報をご記載ください:
- 御社名・業種
- 想定される利用場面
- ご希望のライセンス形態
