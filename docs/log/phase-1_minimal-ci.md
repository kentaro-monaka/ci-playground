# Phase 1: 最小構成のCI構築

- **日付**: 2026-06-07
- **関連コミット/PR**:
    - 0bb4257 fix(test): 最終行のオートインデントを削除
    - 6b7c675 fix(test): コード最後に改行追加
    - b86c2b9 fix(ci): スモークテスト構文修正
    - 357aa30 feat(ci): pytestステップを追加
    - 75faa5e Phase 1 Step3: add lint and ruff
    - f0c4e70 Phase 1 Step2: fix steps
    - fde5bfb Phase 1 Step2: fix
    - 5be0772 Phase 1 Step2: ci.yml with uv setup and uv sync
    - 00d9c02 Phase 1 Step 1: minimal hello workflow"
- **所要時間**:1時間

## 実施内容
- .github/workflowsフォルダを作成
- .github/workflowsにhello.ymlを作成、pushによりActionsが走ることを確認
- .github/workflowsにhello.ymlをci.ymlにリネーム
- ciとしてgit clone、uvセットアップ、依存関係インストール、lint（静的解析）、ruff（書式チェック）、pytest（スモークテスト1件）を実装
- ciの結果が正常に終了することを確認

## ポイント（学んだこと・選択の理由）
- stepsにはname、runなどを実行単位ごとに1つずつブロックを分けて記載する
- pytestはテストがないとエラーになる
- uv.lockをpushすることでgithub上に同じ環境（依存関係含む）を構築することができる

## 詰まったところ
### 詰まり1: ファイル末尾改行の欠落
- **症状**: ruff format --check が `\ No newline at end of file` で exit 1
- **原因仮説**: VS Code 新規ファイル作成時、末尾改行を入れずに保存した
- **解決**: 最終行の後に改行を追加

### 詰まり2: 末尾の trailing whitespace
- **症状**: 改行を追加したつもりだったが、再度 ruff format --check で exit 1
- **原因仮説**: VS Code の auto-indent で「Enter後の自動インデント」が4スペースの空白行を作っていた
- **解決**: 末尾の空白行を手で削除
- **学び**: 「末尾改行」と「行末空白」は別概念。ruff format は両方の検査対象

## 結果
- 最小単位のCIワークフローを構築することができた

## 次の一歩
- Phase 2: ドメイン層の構造とテスト（題材選び+値オブジェクト/エンティティの実装）