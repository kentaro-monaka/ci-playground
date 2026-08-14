# ci-playground ロードマップ

> 本リポジトリの学習活動の全体計画。発表用まとめの土台も兼ねる。
> 確定済みフェーズと **暫定（要確認）** フェーズを区別して記載する。

## 目的（北極星・3本柱）

1. **軽量DDDの実装** — 3層＋ポート方式（domain / application(+ports) / infrastructure）を手を動かして作り切る
2. **CIでの「100%チェック」の仕組み** — 実機なしで全コードが自動検証される品質ゲートを組む
3. **知識として昇華** — 経験を再利用可能な形（`docs/`）に残す。本活動の発表用まとめも兼ねる

知識の保管先は Git 管理下の `docs/`（コンテナ・リビルドでも消えないため）。

### テスト方針（重要）

- カバレッジ **100% は目標として掲げるが、盲目的には追わない**。
- **価値のない確認テストは増やさない**（trivialな行や発生確率の極めて低い例外まで全部埋めることはしない）。意味の薄い箇所は `pragma: no cover` / `exclude_lines` で除外してよい。
- 判断基準は「この行を通すため」ではなく **「この振る舞いを保証するため」**。
- テストの“意味”は行数ではなく **ミューテーションテスト（検出力）** で担保する。
- 全体を通して **学習効率を最優先**する。

---

## システム構成（ポリグロット）

全体は **制御ループ（HMI ↔ ストア ↔ 制御ロジック ↔ フィールドバス ↔ 実機）**。

```
                    [Web UI / HMI]
                nginx + PHP + JavaScript
          表示(読) ↑                 ↓ 設定・指令(書)
   +---------------------------------------------------+
   |            共有データストア（PostgreSQL / Redis）   |
   +---------------------------------------------------+
       センサ値(書) ↑                 ↓ 設定・指令(読)
            [Python DDDアプリ：センサ監視・制御ロジック]
          計測(読) ↑                 ↓ 設定・制御(書)
   +---------------------------------------------------+
   |   フィールドバス・アダプタ                          |
   |   CAN / Modbus(RTU,TCP) / MQTT / HTTPS ...         |
   +---------------------------------------------------+
                        ↕
                 [実機デバイス / センサ]
```

- Python側とWeb側は **直接API連携せず、共有データストア（DB/Redis）経由で疎結合**（Shared Data Store 統合パターン）。
- **ストアへの読み書きは双方向**：UIが設定・指令を書き、Python制御ロジックがそれを読み、**フィールドバスのアダプタで実機に設定・制御を書き込む**。実機のセンサ値はPythonが書き、UIが読んで表示。
- したがって **フィールドバスのアダプタ（CAN/Modbus等）も双方向**：計測の読み取りだけでなく**設定・制御コマンドの書き込み**も担う（Phase 3のポート定義は read/write 両方向前提）。
- **データ所有権**（どのキー/テーブルを誰が書くか）の線引きと、同時書き込み時の**競合/整合性**が論点。
- リポジトリ構成は **monorepo**（`web/` サブディレクトリにWeb側を追加）。
- 最大の検証リスク = Python⇔PHP 双方向の **DB/Redis スキーマ・データ契約**。→ 境界の契約テストを**双方向で**最重要テストとする。

### 想定ディレクトリ構成

```
ci-playground/
├── src/ tests/ pyproject.toml   # Python側（現状）
├── web/                         # nginx + PHP + JS（Phase 7で新規）
├── contract/                    # 境界の契約テスト（Python⇄PHP）
└── ops/                         # docker-compose, CI補助
```

---

## フェーズ一覧

| Phase | テーマ | 状態 | 作業時間（目安） |
|---|---|---|---|
| 0 | 基盤構築（uv / DDD構造 / docログ雛形） | ✅完了 | 2h（実績） |
| 1 | 最小CI（lint→format→pytestスモーク） | ✅完了 | 1h（実績） |
| 2 | ドメイン層（値オブジェクト・エンティティ・集約） | ✅完了 | 5h（実績） |
| 3 | **アダプタ実装**（Python側 infrastructure：全外部依存を実機なしでテスト可能に） | ✅完了（7/7） | 実績に計上 |
| 4 | アプリケーション層（ユースケース／サービス、ポート結線）＋ **構成ルート（DI / composition root）・全体配線** | ✅完了（6/6、CollectReadings/SendReadings/PublishReadings/ApplySetpointをAUX・BMS両系統に配線済み） | 実績に計上 |
| 5 | CI品質ゲート強化（意味のあるカバレッジ※目標100%／型チェック／ミューテーションテスト）※暫定 | 🟡暫定 | 6–10h |
| 6 | 時系列保存・可観測性（InfluxDB 等）※応用 | ⏸保留 | 6–10h |
| 7 | **Web UI ＋ E2E**（nginx+PHP+JS、Playwright、境界契約テスト、ポリグロットCI）※応用 | ⏸保留 | 15–25h |

🟡暫定 = 元の計画から失われた中盤フェーズ。テーマ・順序は要確認（推測で確定していない）。
⏸保留 = 北極星（軽量DDD／CI100%チェック／知識昇華）の達成には必須でない応用編。コア（Phase 0–5）の後、必要になれば着手。

---

## 各フェーズ詳細

### Phase 3：アダプタ実装（実機なしテストの本丸）

Python側 infrastructure 層。アダプタを1つずつ「実機の代替物」に繋いでテスト可能にする。
**3-A で「InMemory Fake ＋ Contract test」の型を作り、以降に使い回す。**
フィールドバス系アダプタ（CAN/Modbus等）は **read/write 両方向**を実装：計測の読み取り＋設定・制御コマンドの書き込み。テストも双方向（書いた制御が仮想デバイスに届くか）で検証する。

Modbus は**役の異なる2つのポート**として実装する（同じ `domain`／契約の型を流用し、`infrastructure` 実装だけ差し替え）：
- **クライアント（マスター）＝ RTU/RS485**：BESS が現場機器（インバータ/BMS）を読み書きする。既存 `FieldBus` ポートの実装。`infrastructure/rs485/`。
- **サーバー（スレーブ）＝ TCP**：上位（EMS/アグリゲータ）が BESS を読み書きする受け口。新規ポート。`infrastructure/modbus/`。
- 当初案の Modbus/TCP クライアントは採用せず（RTU クライアント＋TCP サーバーの構成が実運用に近いため）。

| | アダプタ | 実機の代替手段 | 状態 |
|---|---|---|---|
| 3-A | PostgreSQL / SQLite | docker-compose / `:memory:` | ✅完了 |
| 3-B | Redis | docker-compose / fakeredis | ✅完了 |
| 3-C | HTTPSクライアント | ローカルHTTPモック（respx等） | ✅完了 |
| 3-D | MQTTクライアント | Mosquittoコンテナ | ✅完了 |
| 3-E-1 | Modbus/RTU **クライアント**（BESS→現場機器 / RS485） | 擬似シリアル（pty/socat）＋ pymodbus サーバ | ✅完了 |
| 3-E-2 | Modbus/TCP **サーバー**（上位→BESS / スレーブ） | localhostループバック | ✅完了 |
| ~~3-F~~ | ~~Modbus/RTU~~ → **3-E-1 に統合**（RTU をクライアント本命に採用） | — | 統合 |
| 3-G | CAN（狙いは**アダプタ実装より CI 実行環境の確立**） | python-can `virtual`（常時）＋ SocketCAN `vcan0`（CI で実物） | ✅完了 |

> **3-G の位置づけ**：FieldBus のポートと契約は 3-E-1 で確定済みのため、アダプタ実装自体は反復に近い。本命は「**実機なしの CAN テストを CI で成立させる**」こと（柱②）。
> **環境差の実測（2026-07-20）**：WSL2 カーネルは `CONFIG_CAN=m` / `CONFIG_CAN_RAW=m` だが **`CONFIG_CAN_VCAN` が未設定**のため、手元では vcan を作れない（`--cap-add=NET_ADMIN` を足しても不可。モジュール自体が無い）。GitHub Actions のランナーは `CONFIG_CAN_VCAN=m` だがクラウド向け最小構成で未導入のため、`linux-modules-extra-$(uname -r)` の追加インストールが必要だった。**同じ「vcan が無い」でも原因が異なる**（前者はカーネル再ビルドが要る／後者はパッケージ導入で解決）。
> **解法**：契約に2実装を束ねる。`virtual` はどこでも動く常時実行、`vcan` は実物の SocketCAN。ローカルでは vcan0 の有無を `skipif` で実行時検出して自動スキップ（fakeredis／実Redis と同じ構図）。
> **結果**：ローカル 6 skipped ／ CI 6 passed。手元では不可能な検証を CI が肩代わりする形を確立した。`FieldBus` の6本の契約が Fake / RTU / CAN virtual / CAN vcan の**4実装**で共有されている。

### Phase 4：アプリケーション層（ユースケース＋構成ルート）

＝柱①「DDDを作り切る」の総仕上げ（ポート/アダプタ/ユースケースを結線して動く全体にする）。

**実機構成**：現場機器はCAN／RTUの2系統。**1台の物理機器＝1バス固定**（機器ごとにどちらか一方）。よって `Device` 単体・`CollectReadings` 側の変更は不要で、**構成ルート側が「Device＋対応する FieldBus 実装」のペアをバスの数だけ持ち、バスごとに実行する**。

**上位・外部との対応**：上位（EMS）は Modbus TCP（`ServerBus`）、外部サーバは MQTT（`ReadingSender`）。CAN/RTU からの計測値取り込みは高頻度、MQTT送信・Modbus TCP公開は別周期でよいため、**DBを介して疎結合にする**（Python⇔Web間をDB経由で疎結合にするのと同じ思想を、フィールドバス⇔上位連携の間にも適用）。

| | ユースケース | 内容 | 状態 |
|---|---|---|---|
| 4-A | `CollectReadings` | 実機→`FieldBus.read_reading`→`Sensor.record`→`ReadingRepository.save`。バスの数だけ構成ルートが複数回実行 | ✅完了 |
| 4-B | `RetryingFieldBus` | `FieldBus` 実装を失敗時に自動再試行させるデコレータ | ✅完了 |
| 4-C | `SendReadings` | `ReadingRepository.find_latest`→`ReadingSender.send`（MQTT、外部サーバへ能動送信）。`find_latest` は記録時刻を返さないため `recorded_at` は読み出し時刻（`datetime.now()`）で代用 | ✅完了 |
| 4-D | `PublishReadings` | `ReadingRepository.find_latest`→`ServerBus.publish_reading`（Modbus TCP、EMSが読みに来るレジスタへ受動的に公開） | ✅完了 |
| 4-E | `ApplySetpoint` | `ServerBus.read_setpoint`（EMSの指令を読む）→`Device.setpoint_ranges` の `Range.contains()` で許容範囲チェック→受理時のみ `FieldBus.write_setpoint`（現場機器へ反映）→受理可否を戻り値(`bool`)で呼び出し元に返す。EMS誤指令・通信化けから機器を守る責務をBESS側に持たせる設計判断 | ✅完了（監査ログは見送り、詳細は次項） |
| 4-F | 構成ルート（DI / composition root） | `src/ci_playground/composition_root.py`。付帯設備（RTU接続）・BMS（CAN接続）の2系統を、それぞれ `Device`＋`FieldBus`実装＋`CollectReadings`→`SendReadings`→`PublishReadings`→`ApplySetpoint`で結線。`repository`／`sender`／`server_bus`は`build_composition()`で1回だけ組み立てて両系統に共有する | ✅完了（範囲(i)配線のみ。実行ループ・スケジューリングは対象外、詳細は次項） |

**実行時のスケジューリング（周期実行）は対象外**：構成ルートはオブジェクトグラフの組み立てまでを担う。センサごとに異なる周期での定期実行は「外部からアプリケーションを駆動する」側（Driving Adapter、`entrypoints/`に相当）の責務であり、DDDの構成ルート本来の役割（Driven側の配線）とは向きが逆のため、Phase 4のスコープには含めない。必要になれば`entrypoints/`を新設し、そこから`composition_root`の関数を呼ぶ形で追加する。

**`composition_root`のテスト方針**：ロジックがほぼ無い配線コードを網羅的にユニットテストする価値は低いと判断し、`tests/integration/test_composition_root.py`に「疑似シリアル(socat)＋一時ファイルSQLite＋実Mosquittoで`CollectReadings`→`SendReadings`が一気通貫で動く」smoke testを1本だけ設置。配線ミス（引数取り違え等）は型チェック（Phase 5）で担保し、テストは「実際に動くか」の検証に絞った。`tests/support/rtu_server.py`（`serial_pair`/`modbus_server`フィクスチャ）を`tests/integration/conftest.py`経由で共有し、Phase 3の RTU結合テストと共用している。

**BMS（CAN）系統の追加と共有アダプタ設計**：`build_aux_composition()` は当初、内部で `repository`／`sender` を自前生成していたが、CAN(BMS)系統を追加するにあたりポート型（`ReadingRepository`／`ReadingSender`）の引数として外部から受け取る形に変更した。`ReadingRepository` は `(DeviceId, SensorId)` 単位でキーが分かれるため、AUX（`dev-aux`）とBMS（`dev-bms`）が同一インスタンスを共有しても行が衝突することはない。MQTTクライアント（`sender`）も1本を両系統で使い回すが、`SendReadings.execute()` は呼び出し元が1回ずつ同期的に呼ぶ前提のため、現状のスコープでは並行アクセスの懸念は生じない。トップレベルの `build_composition()` が共有アダプタを1回だけ組み立て、`build_aux_composition()`・`build_bms_composition()` の両方に配って束ねる。

**smoke testの拡張**：`test_composition_root.py` のsmoke testを、AUX単体の検証から `build_composition()` を通してAUX＋BMS両系統を一度に検証する形に置き換えた。BMS側はSocketCAN（`vcan0`）が必要なため、Phase 3で確立した「`vcan0` の有無を `skipif` で実行時検出」という仕組みを再利用。判定関数 `vcan0_exists()` は `test_vcan_field_bus.py` との重複（2箇所目の出現）を機に `tests/support/can_layout.py` へ共通化した。`PublishReadings`追加後は、EMS役の`ModbusTcpClient`でAUX/BMS両方のレジスタ値を実際に読み、公開された値まで検証する形に拡張している。この環境（`vcan0`なし）ではskipされるため、動作確認はCIに委ねる。

**`PublishReadings`の配線とサーバー起動責務の置き場所**：`ServerBus`実装の`TcpServerBus`はEMS向けModbus TCPサーバーを必要とするが、他の`build_*`関数（クライアント接続を1回作るだけ）と違い「非同期イベントループを別スレッドで回し続ける」という重い起動処理を伴う。当初はcomposition_root側に直接書く案だったが、「クライアントの組み立て」ではなく「pymodbusサーバーをどう正しく起動・運用するか」という技術固有の知識と判断し、`TcpServerBus.start(host, port, device_id, sensor_registers, setpoint_registers)`というクラスメソッド（ファクトリ）としてinfra層（`infrastructure/modbus/tcp_server_bus.py`）に実装した。composition_root側の`build_server_bus()`はこれを呼ぶだけの薄い関数になっている。

**データストア選定の訂正**：当初「`pymodbus.simulator`の`SimData`/`SimDevice`は名前からしてテスト専用、本番は`ModbusServerContext`＋`ModbusDeviceContext`＋`ModbusSequentialDataBlock`」と判断したが誤りだった。実装してCIで検証したところ`ModbusSequentialDataBlock(0, [0] * 100)`（先頭アドレス0）が`TypeError: 0 <= address < 65535`でクラッシュし、`ready`の合図が来ないまま`box["server"]`が空の状態で`KeyError: 'server'`になる形で発覚。pymodbus 3.14.0のソース（`datastore/context.py`）を確認すると、`ModbusDeviceContext`は非推奨（v4で削除予定）で、内部では結局`SimDevice`を組み立てて委譲しているだけだった。`pymodbus.simulator`モジュールのdocstring（「experimental、本番非対応」）は移行前の古い記述が残っていたもので、実際のコード（deprecation警告・内部委譲）の方が正しい。教訓：ライブラリのクラス名や一部docstringの見た目だけで判断せず、実装のソースコードで裏取りする。最終的に`SimData`/`SimDevice`を採用し、CIで再現した`KeyError`は解消した。

**EMS向けレジスタ番地の統合**：AUX・BMSどちらの計測値も同じ`TcpServerBus`（1台のサーバー）に公開するため、`EMS_SENSOR_REGISTERS`という1つのマップに両センサの番地をまとめて重複を避けている（RTU側の現場機器内レジスタ番地`AUX_SENSOR_REGISTERS`とは別のModbusコンテキストなので、双方に`address=20`が存在しても衝突しない。EMS向けの1台のサーバー内で番地が重複しないことが重要）。`server_bus`も`repository`／`sender`と同様、`build_composition()`で1回だけ組み立てて両系統に共有する。

**`ApplySetpoint`の配線とAUX/BMSそれぞれの制御対象の見直し**：当初BMS(CAN)側に「電力指令（連続値）」を割り当てる案を出したが、これは誤りだった。BMSはPCS（電力変換装置）ではなくバッテリー保護・監視が役目であり、電力を直接制御する立場にない。実際にCAN側で扱うべきは電磁接触器（MC）のON/OFF指令であり、これはAUX側のリレーON/OFFと同じ「離散的な制御」である。教訓：ユーザーから示された用語（「MC制御」）を自分の思い込み（連続値の力行/回生制御）に寄せて解釈せず、用語の指す実体を確認してから設計する。最終的に両系統とも`Range(0.0, 1.0)`（ON/OFF）の`setpoint_ranges`を`Device`に持たせ、`ApplySetpoint(server_bus, field_bus)`をAUX・BMS双方の構成に配線した。EMS向け`setpoint_registers`（`EMS_SETPOINT_REGISTERS`）と現場機器向け`setpoint_registers`/`setpoint_frames`（`AUX_SETPOINT_REGISTERS`/`BMS_SETPOINT_FRAMES`）は、同じ`setpoint_id`が指す論理的な指令値を別々の物理バス（EMS向けTCP・現場機器向けCAN/RTU）でそれぞれ運ぶ、という構造。

**smoke testでの検証範囲**：`ApplySetpoint`の内部ロジック（範囲チェック・受理可否）は専用unit testで既にカバー済みのため、smoke testでは配線確認に絞り、EMS役の`ModbusTcpClient`で指令値を書き込んだ後`apply_setpoint.execute()`の戻り値（`bool`）が`True`になることだけを確認している。

**ドメイン層の追加**：`Setpoint` エンティティは見送り（状態を持つ主体が不要と判断）。代わりに `Device` に `setpoint_ranges: dict[SetpointId, Range]` を追加し、`Sensor.allowed_range` と対称的に制御点の許容範囲というドメイン知識を保持させた（構成ルート＝インフラ寄りの層に業務ルールを漏らさないため）。

**Modbus応答についての判断**：EMSからの書き込み（FC06/16）はpymodbusの標準動作のまま常にACKを返す（範囲チェックはドメイン層で後追いのため、書き込みトランザクション自体をIllegal Data Value等で拒否することはしない）。EMSへのリアルタイムなステータスフィードバック（専用レジスタでの公開）は見送り、シンプルさを優先。

**監査ログ（`SetpointApplicationRepository`）は実装を見送り**：`ApplySetpoint` は当面、受理可否を戻り値の `bool` で返すだけに留めた。ポート自体の設計（`record(setpoint_id, requested_value, accepted, applied_at)`、書き込み専用、時系列DBの書き込みモデルと素直に対応）は既に検討済みなので、必要になった時点で `ApplySetpoint` に注入して呼び出す形に拡張できる。実装するとしても Phase 4 ではSQL系（既存技術）、時系列DB(InfluxDB等)実装はPhase 6に切り出す方針は維持。

**再確認された技術的負債**（Phase 3から持ち越し・未着手）：
- `Reading` 型エイリアス（`TemperatureReading | VoltageReading | CurrentReading`）が `domain/sensor.py` と `domain/device.py` の2箇所で重複定義（`domain/reading_types.py` は `sensor.py` 側を再輸入する形で依存の向きがやや歪）
- `domain/sensor.py` の `_TYPE_READING_MAP` が `domain/reading_types.py` の `SENSOR_TYPE_TO_READING` と同一内容で重複

### Phase 5：CI品質ゲート強化 ※暫定

- 意味のあるカバレッジ（目標100%だが盲目的に追わない）・型チェック（mypy/pyright）・ミューテーションテスト。＝柱②「CI 100%チェック」の仕上げ。
- テーマ・順序は要確認（推測で確定していない）。

### 保留（応用編）

- ⏸ Phase 6 時系列保存・可観測性（InfluxDB 等）／ Phase 7 Web UI＋E2E。いずれも北極星の達成には必須でないため一旦保留（必要になれば着手）。
- ※「知識昇華」は特定 Phase ではなく、全フェーズ通じて `docs/` に継続。

### Phase 7：Web UI ＋ E2E

- **Web**：nginx + PHP + JavaScript。DB/Redis を **読み書き**（センサ情報の表示＝読み、設定・指令の登録＝書き）。inbound/outbound 両面のアダプタ。
- **E2E**：`@playwright/test`（JS）。テスト対象=JSフロントに言語を合わせる。ヘッドレスChromiumでCI実行＝実機不要。
- **テスト戦略（ピラミッド）**：
  - Web層の大半は **HTTPレベル／各言語unit** で担保
  - **E2E は少数のクリティカルパスのみ**
  - **境界の契約テスト（双方向）**（Python書込→PHP読取／PHP書込→Python読取、両方向の整合）を最重要テストとして設置
- **ポリグロット・カバレッジ**：Python(`pytest-cov`) / PHP(`PHPUnit`+PCOV) / JS(`c8`等) の3系統をCIで束ねる（数値合わせの無駄テストはせず、意味のある範囲で）。
- **CI実行**：`docker compose`（nginx + php-fpm + postgres + redis）で全部コンテナ完結＝実機ゼロ。

---

## 作業時間サマリ

| 区分 | 時間（目安） |
|---|---|
| 完了済み（Phase 0–3：アダプタ7種すべて） | 約 18h ＋ 3-E〜3-G 分（実績・要記入） |
| Phase 4（アプリ層＋構成ルート） | 8–12h |
| Phase 5（CI品質ゲート） | 6–10h |
| **北極星コア 残り合計** | **約 14–22h** |
| ⏸保留：Phase 6（時系列・可観測性） | 6–10h |
| ⏸保留：Phase 7（Web＋E2E） | 15–25h |

> 前提：ソロ学習ペース。実装だけでなく **学習・調査・詰まり対応・docログ記録** を含む実績ベース。
> 北極星コア＝Phase 0–5。Phase 6/7 は保留（応用編）。着手すれば +21〜35h。
> 暫定フェーズ（4–5）はテーマ未確定のため時間幅も粗い。確定すれば精緻化する。

---

## 凡例

- ✅完了 / 🔄進行中 / 🟡暫定（要確認） / ⏸保留（応用編・北極星に必須でない）
- 暫定フェーズは、元の計画から失われた部分。推測で固定せず、進めながら確定していく。
- 保留フェーズ（6/7）は、北極星3本柱の達成には不要な応用編。コア（0–5）完了後に必要なら着手。
