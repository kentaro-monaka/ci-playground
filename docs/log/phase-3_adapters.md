# Phase 3: アダプタ実装（DB）－ 契約テスト ＋ DB(Fake/SQLite/Postgres/Redis) ＋ HTTPS送信

- **日付**: 2026-06-13, 2026-06-14～2026-06-20
- **関連コミット/PR**:
    - da754d6 feat(test): HttpReadingSender を respx で検証するテストを追加
    - d765b97 feat(infrastructure): Reading を HTTPS で送信する Adapter を追加
    - fe6ded3 feat(application): ReadingSender ポートと ReadingSendError を定義
    - cbe09bf feat(dev): httpx、respxを追加
    - 0413627 fix(test): Redis テストの import 整形と decode_responses 引数名を修正
    - 0a029ee docs(roadmap): Phase 3-B を完了
    - 8faff40 docs(log): Phase 3-B のログを追記
    - 1d7ba0c feat(ci): docker-compose に Redis を追加
    - fc2600f feat(test): Redis アダプタを契約テストに束ねる（fakeredis/実Redis）
    - d826c02 feat(infrastructure): Reading を Redis に保存・取得する Adapter を追加
    - f03e88d docs(roadmap): Phase 3-A を完了
    - 8bb5398 docs(log): Phase 3-A のログを作成
    - ff037c6 feat(ci): docker-compose の Postgres を CI で起動して統合テストを実行
    - 7cf245d feat(test): 実Postgres を契約テストに束ねる（docker マーカー登録）
    - f7e532e fix(test): SQLite フィクスチャで engine を破棄し ResourceWarning を解消
    - 329fee2 chore(dev): VS Code の Python 解析設定（extraPaths）を追加
    - eecc50c feat(test): ReadingRepository の契約テストと Fale/SQLite 束ねを追加
    - a593ca5 feat(infrastructure): InMemory Fake の ReadingRepository を追加
    - b33eaa6 fix(infrastructure): コメント修正
    - 79849ed fix(infrastructure): find_latest の逆引き辞書を修正し Adapter を sqlAlchemy にリネーム
    - a224023 docs(roadmap): DBのテストをdockerコンテナを使う方式に変更
    - 9f3b753 docs(roadmap): 全体のロードマップを作成
    - aa01965 feat(infrastructure): Postgres 版 ReadingRepository Adapter を追加
    - fec843a feat(infrastructure): DB engine と Session factory を追加
    - 218279c feat(infrastructure): SQLAlchemy ORM モデル（ReadingRow）を追加
    - d531bed feat(application): ReadingRepostory ポートを定義（Protocol）
- **所要時間**: 5時間

## 実施内容
- ポート定義：application/ports/reading_repository.py に ReadingRepository（Protocol）を定義。save / find_latest の抽象シグネチャ
- ORM モデル：infrastructure/db/orm.py に ReadingRow（readings テーブル：id/device_id/sensor_id/sensor_type/value/recorded_at + 複合インデックス）。ドメイン型とは別のDB一対一マッピング
- 接続基盤：infrastructure/db/connection.py に get_engine（URL or DATABASE_URL）と session_factory（expire_on_commit=False）
- SQLAlchemy アダプタ：save（ドメイン⇒ReadingRow⇒commit）、find_latest（DBから検索してドメインに復元）
- tests/contract/reading_repository_contract.py に抽象 Contract test（4約束：保存から取得、空ならNone、latest最新が勝つ、別の device/sensor のデータが混ざらない）作成
- インメモリに保存するFake のリポジトリ（InMemory Fake）を作成し、契約に束ねた
- SQLite（:memory, StaticPool） を同じ契約に束ねる
- find_latest の逆引き辞書バグ修正（_SENSOR_TYPE_TO_READING 追加）
- 実Postgres を ops/docker-compose.yml で用意⇒契約に束ねる（@pytest.mark.docker）
- fixtureのDBクローズ漏れに対応して return から try + finally に変更し engine.dispose()でResourceWarning解消
- CI に compose-Postgres 起動ステップ追加
- コンテナリビルドによりclaude履歴が消えたためdocs/roadmap.md をgit管理追加
- Redis アダプタを契約テスト＋複数実装の型に追加。RedisReadingRepositoryを実装。
- tests/unit/infrastructure/redis/test_fakeredis_reading_repositoryを実装、docker不要のユニットテスト。
- tests/integration/infrastructure/redis/test_redis_reading_repositoryを実装、docker要の統合テスト。
- CI で起動する docker-compose.yml に redis起動設定を追加
- ポート定義：application/ports/reading_sender.py に ReadingSender（Protocol）と専用例外ReadingSendError を定義。
- アダプタ定義：infrastructure/https/http_reading_sender.py
- respx テスト3本（unit・docker不要）：正常系、500エラー、接続タイムアウト。

## ポイント（学んだこと・選択の理由）
- 契約テストにより1つの仕様を3実装でテストできる（Fake/SQLite/実Postgres）
- pytestには収集対象になる命名規則がある、ファイルの場合test_*、クラスの場合Test*、メソッドの場合test_*が自動収集される
- 契約テスト時の親（仕様）ファイルは接頭語なしで収集させず、メソッドだけtest_*で子が継承して走らせることができる
- DBのFakeの場合、オブジェクトのままlistに保持するなど簡易化して実装する。検索もSQLなしで契約のみ満たすように簡易に実装する。
- SQLiteはサーバーレスのRDBであるため、SQLAlchemy が engine URL で 接続先を切り替えるだけでpostgresと同一アダプタで対応可能
- SQLite:memory:は engine 新規=自動で空になる。実Postgresは永続するので毎テストdrop_all、create_allで掃除する。
- CIとローカルで同じymlファイルからcomposeすることで環境差がなくなる
- fixture ＝ "毎回同じ条件を固定して用意する治具"。ソフトでは「テスト前に整える準備済みの土台」、pytest ではそれを作る関数。
- 後始末の有無＝本物の接続を持つかで決まる：fakeredis は return（資源なし）、実Redis は yield＋client.close()（実接続あり）。3-A の engine.dispose()と同じ理屈。
- 失敗が起きない箇所（単に文字列を返すだけ）などはtry、except で例外処理を書くとバグを隠してしまうため不要なら使わない。
- docker-composeでは`CMD-SHELL`を使うときは コマンドを1文で書く、`CMD` を使うときはコマンド毎に区切る。
- httpx の失敗2系統：非2xx は既定で例外を投げない→raise_for_status() が必要。
- respx を使うことで実通信なしでサーバ側のふるまいをテストコード内で使うことができる。

## 詰まったところ
### 詰まり1: コンテナリビルドで uv/Python が消失
- **症状**: uv: command not found、python3も無い
- **原因**: devcontainer にPython feature が無く、ツールチェインは~/.localにあってリビルドで消えた
- **解決**: uv 再インストール ⇒ uv sync --all-groups で .venv（3.13.14）再生成

### 詰まり2: VS Code の予測変換が出ない
- **症状**: 補完が効かない
- **原因**: Python拡張・Pylance が ~/.vscode-server ごと消えた
- **解決**: 再インストール ⇒ インタプリタに .venv/bin/python を選択

### 詰まり3: ci_playground.* の import に赤線
- **症状**: 自作パッケージだけ Pylance が解決できず赤線（sqlalchemy等は解決できる）
- **原因**: pytest は pythonpath["src"]で動くがPylanceはpytest設定を読まない。パッケージは venv にも入っていない。
- **解決**: .vscode/settings.json に python.analysis.extraPaths=["src"]
- **学び**: リビルド前に効いていた設定は ~/.vscode-server 側にあったかもしれない。repo内に置けば残る。

### 詰まり4: find_latest の逆引きバグ（本セッション最大の収穫）
- **症状**: KeyError: <SensorType.TEMPERATURE> save 後のfind_latestで。
- **原因**: _READING_TO_SENSOR_TYPE(Readingクラス⇒SensorType)を、逆向き(SensorType⇒Readingクラス)が必要な場面で引いた。
- **解決**: 逆引き辞書 _SENSOR_TYPE_TO_READING を辞書内包で生成。

### 詰まり5: ResourceWarning: unclosed sqlite3 connection
- **症状**: テスト後に ResourceWarning
- **原因**: SQLite フィクスチャが engine(StaticPoolで1接続保持)を**dispose()していない**
- **解決**: フィクスチャをtry + finally にして最終的にengine.dispose()　で閉じる


## 結果
- domain 62 ＋ 契約(4×5実装) 20 + HTTPS送信 3 ＝ 85 passed、カバレッジ 93.51%
- unit/integration を docker要否で確定、-m "not docker"で高速ループ
- CI に dockerコンテナ（postgreSQL + Redis）を使ったDBテストを追加することができた
- CI に respx を使ったhttps 通信テストを追加することができた


## 次の一歩
- Phase 3-D: MQTTクライアント追加