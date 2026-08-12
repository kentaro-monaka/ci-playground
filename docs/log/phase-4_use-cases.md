# Phase 4: アプリケーション層（ユースケース）＋構成ルート

- **日付**: 2026-08-12
- **関連コミット/PR**:
    - e84c886 (HEAD -> main) docs(roadmap): Phase 4 (ユースケース+構成ルート) を完了として更新
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

## ポイント（学んだこと・選択の理由）
- 構成ルートはロジックがほぼ無い配線コードなので、網羅的なユニットテストではなく「実際に動くか」を確認するsmoke test 1本に絞った。
- SQLiteのin-memory URLは接続ごとに別DBになる問題があるため、smoke testでは一時ファイルDBを使用
- Modbus書き込みは常にACK（pymodbus標準動作のまま）、範囲チェックはアプリケーション層で後追い。
- **assertの無いテストは「配線が繋がっているか」しか検証できず「正しい値が流れているか」を見落とす**
- pytestのfixtureをテストファイル間で共有するには`conftest.py`に置くのが正解。テストファイルへ直接importするとruffのF811（redefinition）に引っかかる（pytestのfixture解決とruffの静的解析の食い違い）
- 構成ルートは配線作業に間違いがないことを確認するためにテストが必要。テストしない場合、全体のカバレッジが低下する。

## 詰まったところ
### 詰まり1: composition_root.py がカバレッジ0%で全体カバレッジ89%まで低下
- **症状**: `pytest --cov`実行時、`composition_root.py`(46 stmts)が丸ごと未カバーで全体89%（Phase 3終了時94%から低下）
- **原因仮説**: 構成ルートを組み立てただけで、実際に実行するテストが無かった
- **解決**: `test_composition_root.py`のsmoke testで実行され、該当ファイル100%カバー、全体97%まで回復

## 結果
- Phase 4 全項目完了（4-A〜4-F）
- 全体テスト 138 passed / 6 skipped（vcan未対応環境のためskip、既知）
- カバレッジ 97%
- lint/format 全ファイルクリーン

## 次の一歩
- Phase 5: CI品質ゲート強化（型チェック mypy/pyright、ミューテーションテスト）
- 技術的負債：`Reading`型エイリアスの重複（`domain/sensor.py`/`domain/device.py`）、`_TYPE_READING_MAP`の重複解消
- 構成ルートのCAN系統・`PublishReadings`/`ApplySetpoint`経路の横展開（同じパターンで未着手のまま）