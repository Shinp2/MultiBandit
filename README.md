# MultiBandit

このリポジトリは多腕バンディット実験を行うためのスクリプト群を含みます。主なスクリプトと使い方を以下にまとめます。

## 概要
- `Multibandit.py` : 実験のメイン Python スクリプト（平均報酬の計算やプロット出力などを行います）。
- 補助スクリプトは `../shell/run_experiment.sh`（ワークフロー用ラッパー）や `../python/experiment_ar.py` にあります。

## 依存関係
- Python 3.x
- numpy
- matplotlib

インストール例（Debian/Ubuntu）:
```fish
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy matplotlib
```

## 使い方（基本）
リポジトリのルートで以下のように実行します。`Multibandit.py` は必要に応じて引数を持つので、ヘルプを参照してください。

```fish
python3 programs/MultiBandit/Multibandit.py --help
```

（このプロジェクトには複数の実験ドライバがあるため、実行例をいくつか示します。）

### 例: 単一実行
```fish
python3 programs/python/experiment_ar.py --K 10 --fixed-time 1000 --repeats 20 --out ar_single.png
```

### 例: 複数の epsilon を試す
（ラッパーを使うと楽です）
```fish
bash programs/shell/run_experiment.sh --epsilons 0.01 0.05 0.1 --fixed-time 6500 --repeats 30 --out ./sample.png
```

### 例: K 列のスイープ
```fish
python3 programs/python/experiment_ar.py --Ks 10 50 100 --fixed-time 2000 --repeats 10 --out Ks_vs_ar.png
```

### 例: ファイルで theta を与える（1行ずつ別プロット）
```fish
# theta.txt に各行が1つの theta 設定（カンマ区切り等 ラッパーのフォーマット参照）
bash programs/shell/run_experiment.sh --theta-file-lines theta.txt --repeats 10 --out theta_{n}.png
```

## 出力
- プロット画像（PNG）やログを出力します。`--out` オプションで出力ファイルを指定できます。

## トラブルシュート
- `Permission denied (publickey)` が出る場合は SSH 鍵が GitHub に登録されているか確認してください。`ssh -T git@github.com` で接続テストできます。
- ラッパーでエラーが出る場合は、まず Python 側のスクリプトを直接 `--help` で確認して、必要な引数が渡されているか確認してください。

## 開発メモ
- ブランチ運用: デフォルトブランチは `main` です。ローカルに `master` のコミット履歴がある場合、マージや履歴統合の手順が必要になります。

## ライセンス
- このリポジトリのライセンスはプロジェクトに合わせて設定してください（必要なら `LICENSE` を追加してください）。

---
もし README に追記してほしい点（例: 実行パラメータの詳細、入出力フォーマットの具体例、よくあるエラーと解決法）があれば教えてください。追記します。
# MultiBandit