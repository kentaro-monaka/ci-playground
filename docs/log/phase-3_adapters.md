# Phase 3: アダプタ実装（DB）－ 契約テスト ＋ DB(Fake/SQLite/Postgres/Redis) ＋ HTTPS送信

- **日付**: 2026-06-13, 2026-06-14～2026-06-25, 2026-07-17〜2026-07-20
- **関連コミット/PR**:
    - 7b8940b feat(test): 上位役クライアントで TCP ServerBus の線越し往復を検証
    - 612dea4 feat(test): TCP ServerBus を実サーバーに束ね契約を通す
    - a7d4907 feat(infrastructure): Modbus/TCP の ServerBus アダプタを実装
    - bf6fe43 refactor(infrastructure): modbus_registers に docstring を追加し整形
    - 6de8ae2 refactor(infrastructure): RegisterSpec を共有モジュールに切り出し RTU/TCP で共用
    - 2ef7cf4 feat(test): ServerBus 契約テストを追加し InMemory Fake を束ねる
    - 3e1f31a feat(infrastructure): InMemory Fake の ServerBus を追加
    - faf4855 feat(application): ServerBus ポートと ServerBusError を定義
    - e7ab577 docs(roadmap): 3-E-1 を完了
    - acff046 docs(log): Phase 3-E-1 Modbus RTUクライアントのログを追記
    - fe92a8b feat(ci): 疑似シリアル用に socat を導入し RTU 結合テストを CI で実行
    - c483d57 feat(test): RTU FieldBus に read_reading を実装し契約6本フルで束ねる
    - eb5dec5 feat(test): RTU FieldBus を実pymodbusサーバーに束ね setpoint 契約を通す
    - d4e5f34 feat(infrastructure): RTU FieldBus アダプタに setpoint 読み書きを実装
    - c9e9378 docs(roadmap): 3-E を RTUクライアント+TCPサーバーに再構成、3-F統合・3-G保留
    - 357dd4b feat(dev): pymodbus の serial extra を追加（RTU クライアント用）
    - 263b11f feat(test): FieldBus 契約に read_reading の約束を追加し未知IDの穴を塞ぐ
    - ab04636 feat(test): FieldBus 契約に setpoint の未書込・未知IDの約束を追加
    - 6ee825c feat(test): FieldBus 契約テストを追加し InMemory Fake を束ねる
    - ec37123 feat(infrastructure): InMemory Fake の FieldBus を追加
    - a40b173 feat(application): FieldBus ポートと FieldBusError を定義
    - 64086ee feat(domain): SetpointId を追加
    - 290fe5e feat(dev): pymodbusを追加
    - 5c063f1 feat(test): ReadingSenderContract を抽出し HTTPS/MQTTを契約テストで束ねる
    - c37c4da refactor(infrastructure): 送信ペイロードを reading_to_payload に共通化（HTTPS/MQTT 共用）
    - 4f138de feat(ci): docker-compose に Mosquitto を追加し MQTT 統合テストを追加
    - 0afc2ee feat(test): MqttReadingSender の unit テスト（pahoをモック）を追加
    - 90e4b1c feat(infrastructure): MQTT 送信アダプタ MqttReadingSender を追加（paho-mqtt）
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
- **所要時間**: 18時間

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
- アダプタ定義：infrastructure/https/http_reading_sender.py。HTTPSのアダプタ。
- respx テスト3本（unit・docker不要）：正常系、500エラー、接続タイムアウト。
- アダプタ定義：infrastructure/mqtt/mqtt_reading_sender.py。MQTTのアダプタ。
- unit：respx 相当が無いので paho Client を unittest.mock でまるごと偽装、topic/payload/qos を検証＋失敗仕込み。
- integration：ops/mosquitto.conf（listener+匿名許可）＋ compose に Mosquitto、実ブローカへ送れること（PUBACK受領）を確認。
- 【リファクタリング】 reading_to_payload を infrastructure/reading_payload.py に切り出し、HTTP/MQTT 両方が使用（dict まで共通・JSON化は各輸送）。
- 【リファクタリング】 ReadingSenderContract（成功＝静か／失敗＝例外の2本）を作り HTTP/MQTT が継承。子は sender_ok/failing_sender を供給。payloadと固有の失敗経路は個別に残す。
- domain: `SetpointId` 値オブジェクトを追加（`SensorId`/`DeviceId` と同型）。
- ポート定義: `application/ports/field_bus.py` に `FieldBus` (Protocol・read_reading/write_setpoint/read_setpoint の3メソッド) と `FieldBusError` を定義
- InMemory Fake: `infrastructure/memory/in_memory_field_bus.py`。setpoint は dict、reading はコンストラクタ注入、存在集合で未知判定
- 契約テスト： `tests/contract/field_bus_contract.py` に6本 (setpoint往復／未書込0.0／未知read・write→例外／reading読取／未知reading→例外)
- RTU実アダプタ： `infrastructure/rs485/rtu_field_bus.py`。`ModbusSerialClient`、`RegisterSpec`(address/scale/sensor_type)をコンストラクタ注入
- CI： `ci.yml` に socat インストールを追加
- ポート定義： `application/ports/server_bus.py` に `ServerBus` (Protocol・publish_reading/read_setpoint の2メソッド)と `ServerBusError` を定義
- InMemory Fake: `infrastructure/memory/in_memory_server_bus.py`。setpoint はdict、既知センサは集合で判定
- 契約テスト： `tests/contract/server_bus_contract.py` に4本追加
- 【リファクタリング】`RegisterSpec` を `infrastructure/modbus_register.py` に切り出し、RTU/TCP 両アダプタを共用
- TCP実アダプタ： `infrastructure/modbus/tcp_server_bus.py`。サーバーとイベントループを注入。
- 結合テスト： `ModobusTcpServer` を 127.0.0.1:5020 に立て契約4本を束ねる（ローカルループバックのためCIでの環境追加不要）


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
- MQTTはクライアントからのデータ送信時にブローカ経由で publish する。URLの代わりにtopicとしてパスを指定する。
- QoS1＋wait_for_publish＝「本当に届いた(PUBACK)」＝HTTP の 2xx 相当。
- assert 無しテストの意味：例外が出なければ pass（send が失敗時 raise するので、最後まで到達＝成功）。
- 共通関数への抽出は2つ目が出てから（早すぎる抽象化回避）。
- 送信契約は薄い（2本）。payload 検証は輸送依存で契約に入れられない。
- Mosquitto 2.x は既定で匿名拒否→conf で listener＋allow_anonymous。healthcheck は mosquitto_pub。
- ポート/契約は輸送方法に非依存=TCP/RTUの差は infrastructure の実装クラス1個だけ。domain・ports・契約は無変更で流用できる
- pymodbusサーバーは非同期（asyncio）=ただのスレッドでは `no running event loop`。スレッド内で `asyncio.run(main())` してループを用意、停止は `run_coroutine_threadsafe` (別スレッドのループへ投げる)
- pty番号は動的割当=fixtureは socat の stderr 出力から正規表現で取得しハードコートしない。
- pyserial は最新3.5 (2020-11)で更新停止だが、シリアルは枯れた領域+pymodbusが依存指定で代替なし。「更新停止=即危険」ではなく対象領域の変化速度と依存元の判断で評価。
- 後始末：実シリアルは `client.close()`、socatは `terminate()`、サーバーは `shutdown()`
- 技術的負債=Reading⇔SensorType 対応表が4ファイル重複 (reading_payload/sqlalchemy/redis/rtu)。真の重複なので domain へ共通化予定（別回・別コミット）
- 別途: RTU の isError→FieldBusError 翻訳を固有テストで担保（現状カバレッジ 89%、未カバー rtu_field_bus.py:57/68/80）
- pymodbus のサーバー側 datastore API は async 専用。一方クライアントAPIは同期。
- TCP はループバックで完結するので socat も compose も不要。CI は無変更で新テストを拾う


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

### 詰まり6: Modbus サーバー生成で `RuntimeError: no running event loop`
- **症状**: `ModbusSerialServer(...)` を別スレッドで生成した瞬間に落ちる
- **原因**: pymodbus サーバーは非同期。生成時に `asyncio.get_running_loop()` を呼ぶがループが無い
- **解決**: スレッド内で `asyncio.run(main())` を回し、その中で生成・`serve_forever`。停止は `run_coroutine_threadsafe`

### 詰まり7: `ModuleNotFoundError: No module named 'tests'`
- **症状**: 新テストが `from tests.contract...` の import で収集エラー
- **原因**: 新ディレクトリ `tests/integration/infrastructure/rs485/` に `__init__.py` が無く、`tests` パッケージが解決できない
- **解決**: 空の `__init__.py` を追加

### 詰まり8: read_reading で `ExceptionResponse code=2`（Illegal Data Address）
- **症状**: reading契約だけ失敗。番地20で例外応答
- **原因**: サーバーの `SimData` が番地10-17しか定義しておらず、sensor用の番地20が未定義。
- **解決**: `SimData` を2ブロック（setpoint域10-17＋sensor域20に250）にして device に渡す。TCPループバックで挙動を先に検証してから修正

### 詰まり9: `ModbusSerialClient` が `RuntimeError`（pyserial 未導入）
- **症状**: RTUクライアント生成で失敗
- **原因**: pymodbus 3.x はシリアルを optional extra 化。本体だけでは pyserial が入らない
- **解決**: `uv add "pymodbus[serial]"`

## 結果
- domain 65 ＋ 契約(4×5実装) 20 ＋ FieldBus契約(6×2実装) 12 + ServerBus契約(4×2実装) 8 + 線越し往復 2 + HTTPS 4 ＋ MQTT unit 4 ＋ MQTT integration 1 ＝ 116 passed、カバレッジ 93.75%
- unit/integration を docker要否で確定、-m "not docker"で高速ループ
- CI に dockerコンテナ（postgreSQL + Redis）を使ったDBテストを追加することができた
- CI に respx を使ったhttps 通信テストを追加することができた
- CI に socat を使ったModbusRTU 通信テストを追加することができた
- Modbus/TCP サーバーはループバック完結のため CI 無変更で通る（socat・コンテナ不要）


## 次の一歩
- Phase 3-G: CAN。狙いはアダプタ実装ではなく **実機なしの CAN テストを CI で成立させること**（柱②）。FieldBus のポート・契約は 3-E-1 で確定済みのため新規設計はほぼ無い
