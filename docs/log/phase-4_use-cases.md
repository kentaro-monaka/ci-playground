# Phase 4: アプリケーション層（ユースケース）＋構成ルート

- **日付**: 2026-08-12～14
- **関連コミット/PR**:
    - b92ef34 feat(composition): ApplySetpointをAUX/BMS両系統に配線
    - 494504e docs(roadmap): modbusデータストア選定の経緯を追記
    - 548bc66 fix(infrastructure): TcpServerBus.start() のデータストアを SimData/SimDevice に修正
    - 8e48427 docs(roadmap): PublishReadings配線の経緯を反映
    - ff12441 test(integration): smoke testでpublish_readingsまで検証するよう拡張
    - 35ba025 feat(composition): PublishReadingsをAUX/BMS両系統に配線
    - 84a521f feat(infrastructure): TcpServerBus.start() ファクトリを追加
    - dc1dde2 test(integration): composition_rootのsmoke testをAUX+BMS両系統版に更新
    - 184866e refactor(test): vcan0存在チェックのテスト間共通化
    - 2e79389 feat(composition): BMS (CAN) 系統の追加＋共有アダプタで束ねるbuild_composition()新設
    - 4e02201 docs(log): Phase 4 ユースケース+構成ルートのログを追記
    - e84c886 docs(roadmap): Phase 4 (ユースケース+構成ルート) を完了として更新
    - 6bd96be feat(composition): 付帯設備(RTU)向け構成ルートを組み立て CollectReadings→SendReadings を結線
    - 9b29d7a refactor(test): RTU結合テストの疑似シリアル/サーバーフィクスチャを共通化
    - 1097c9c feat(application): EMS指令を検証し現場機器へ反映する ApplySetpoint を追加
    - cd76661 feat(domain): Device に制御値の許容範囲 setpoint_ranges を追加
    - 8b12006 feat(application): DB最新値をEMS向けに公開する PublishReadings を追加
    - 83ccbf5 feat(application): DB最新値をMQTTで送信する SendReadings を追加
- **所要時間**: 3時間

## 実施内容
- ポート定義：application/ports/{field_bus, reading_sender, server_bus, reading_repository}.py（既存4ポート）を使い回し、4ユースケースを実装
- `SendReadings`：`ReadingRepository.find_latest`→`ReadingSender.send`（MQTT）。`find_latest`が記録時刻を返さないため`recorded_at`は読み出し時刻（`datetime.now()`）で代用
- `InMemoryFakeReadingSender`：送信履歴を`sent`リストに保持するFake（infrastructure/memory/in_memory_reading_sender.py）
- `PublishReadings`：`ReadingRepository.find_latest`→`ServerBus.publish_reading`（Modbus TCP、EMS向け受動公開）
- `InMemoryFakeServerBus`に検証用の`published`リストを追加（既存契約テストへの影響なしを確認済み）
- `ApplySetpoint`：`ServerBus.read_setpoint`→`Device.setpoint_ranges`の`Range.contains()`で範囲チェック→受理時のみ`FieldBus.write_setpoint`→受理可否を戻り値`bool`で返す
- domain: `Device`に`setpoint_ranges: dict[SetpointId, Range]`を追加（`Setpoint`エンティティ化は見送り）
- 構成ルート：`composition_root.py`に付帯設備（RTU接続）の`Device`／`RtuFieldBus`／`SqlAlchemyReadingRepository`／`MqttReadingSender`を組み立て、`build_aux_composition()`で`CollectReadings`→`SendReadings`を結線
- テスト：`tests/support/rtu_server.py`にRTU結合テスト用フィクスチャ（`serial_pair`/`modbus_server`）を切り出し、`tests/integration/conftest.py`で共有（Phase 3の`test_rtu_field_bus.py`と共用）
- `tests/integration/test_composition_root.py`にsmoke testを追加（疑似シリアル＋一時SQLite＋実Mosquittoで一気通貫。DB保存値・last_readingまでassertで検証）
- composition_rootにBMS（CAN接続）系統を追加。`build_bms_device`/`build_can_field_bus`/`BmsComposition`/`build_bms_composition`を新設
- `build_aux_composition()`の`repository`/`sender`をポート型引数化し、`build_composition()`でAUX/BMS共有のアダプタを1回だけ組み立てて両系統に配る設計に変更
- `vcan0_exists()`を`tests/support/can_layout.py`へ共通化（`test_vcan_field_bus.py`との重複解消、2箇所目の出現を機に）
- `PublishReadings`をAUX/BMS両系統に配線。EMS向け`TcpServerBus`は`TcpServerBus.start()`というクラスメソッド（ファクトリ）としてinfra層に実装し、composition_rootは薄い呼び出しだけに留めた
- `ApplySetpoint`をAUX（リレーON/OFF）・BMS（電磁接触器MC ON/OFF）両系統に配線。
- smoke testを段階的に拡張：AUX単体→AUX+BMS両系統→`PublishReadings`検証（`ModbusTcpClient`でレジスタ読み出し）→`ApplySetpoint`検証（戻り値`bool`の確認）

## ポイント（学んだこと・選択の理由）
- 構成ルートはロジックがほぼ無い配線コードなので、網羅的なユニットテストではなく「実際に動くか」を確認するsmoke test 1本に絞った。
- SQLiteのin-memory URLは接続ごとに別DBになる問題があるため、smoke testでは一時ファイルDBを使用
- Modbus書き込みは常にACK（pymodbus標準動作のまま）、範囲チェックはアプリケーション層で後追い。
- **assertの無いテストは「配線が繋がっているか」しか検証できず「正しい値が流れているか」を見落とす**
- pytestのfixtureをテストファイル間で共有するには`conftest.py`に置くのが正解。テストファイルへ直接importするとruffのF811（redefinition）に引っかかる（pytestのfixture解決とruffの静的解析の食い違い）
- 構成ルートは配線作業に間違いがないことを確認するためにテストが必要。テストしない場合、全体のカバレッジが低下する。
- サーバー起動（非同期イベントループ管理）は「クライアントを組み立てる」ような軽い配線作業とは性質が異なり、「特定技術をどう正しく運用するか」というinfra層の知識と判断。composition_rootには薄い呼び出しだけを残した

## 詰まったところ
### 詰まり1: composition_root.py がカバレッジ0%で全体カバレッジ89%まで低下
- **症状**: `pytest --cov`実行時、`composition_root.py`(46 stmts)が丸ごと未カバーで全体89%（Phase 3終了時94%から低下）
- **原因仮説**: 構成ルートを組み立てただけで、実際に実行するテストが無かった
- **解決**: `test_composition_root.py`のsmoke testで実行され、該当ファイル100%カバー、全体97%まで回復
#### 詰まり2: `TcpServerBus.start()`がCIで`KeyError: 'server'`
- **症状**: CI上で`test_composition_collects_and_sends_both_systems`が`KeyError: 'server'`で失敗
- **原因**: `ModbusSequentialDataBlock(0, [0]*100)`の先頭アドレス0が内部で`address-1`に変換され、`SimData`の検証（`0<=address<65535`）に失敗してバックグラウンドスレッドがクラッシュ。`ready`の合図が来ないまま`box["server"]`が空で`KeyError`
- **解決**: 先頭アドレスを1にするだけでも`ModbusSequentialDataBlock`側のクラッシュ自体は解消することを確認したが、その過程で`ModbusDeviceContext`系が非推奨（v4で削除予定）という警告に気づいた。pymodbusのソース（`datastore/context.py`）を確認すると、内部的に結局`SimData`/`SimDevice`へ委譲しているだけのラッパーだったため、アドレスの帳尻合わせでは根本対応にならないと判断し、直接`SimData`/`SimDevice`を使う実装に切り替えた（`SimData`はアドレス変換を行わないため、`0`始まりのままで動く）

## 結果
- Phase 4 全項目完了（4-A〜4-F）
- 全体テスト 138 passed / 6 skipped（vcan未対応環境のためskip、既知）
- カバレッジ 97%
- lint/format 全ファイルクリーン
- 構成ルートの横展開が完了：`CollectReadings`→`SendReadings`→`PublishReadings`→`ApplySetpoint`の4ユースケース全てがAUX・BMS両系統に配線済み

## 次の一歩
- Phase 5: CI品質ゲート強化（型チェック mypy/pyright、ミューテーションテスト）
- 技術的負債：`Reading`型エイリアスの重複（`domain/sensor.py`/`domain/device.py`）、`_TYPE_READING_MAP`の重複解消