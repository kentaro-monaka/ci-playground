# Phase 0: プロジェクト基板構築（リポ作成・uv・ディレクトリ・ドキュメント雛形）

- **日付**: 2026-06-06
- **関連コミット/PR**:
    - 10015eb Phase 0: project scaffolding (uv, DDD layered structure, doc template)
- **所要時間**:2時間

## 実施内容
- GitHubで学習用リポジトリ（ci-playground）作成
- cloneでdevcontainer内にリポジトリの内容をコピー
- uv インストール、uv 初期化 `uv init --python 3.13`
- ディレクトリ構造作成（軽量DDD、3層+ポート方式）
- 開発依存関係追加（pytest, pytest-cov, ruff）

## ポイント（学んだこと・選択の理由）
- 軽量DDDの場合、portsはapplication層に入れて輸出契約を集約する（独立portsにすると責務が曖昧になる）
- pytest-covはカバレッジ計測ツール。初期に入れることで早期からカバレッジを意識する

## 詰まったところ
### 詰まり1: uv未インストール
- 症状: uv init 実行時に command not found
- 原因: uv が DevContainer に同梱されていなかった
- 解決: curl で install スクリプト実行

### 詰まり2: 権限エラー
- **症状**:uv初期化コマンドが権限エラーになった
- **原因仮説**:git clone時にsudo実行したためroot権限になっていたことが原因
- **解決**:chownで所有者を変更し実行したところ初期化成功

## 結果
- ディレクトリ構造が完成
- uvの初期化、開発依存関係追加完了

## 次の一歩
- git push