# Phase 2: ドメイン層データクラス定義とテスト

- **日付**: 2026-06-07
- **関連コミット/PR**:
    - 16c4e2f feat(test): 電流データクラスに対する無限大、NaN例外テスト追加
    - 1b6b1aa fix(domain): 電流データクラスのmathインポート忘れ対応
    - eacb6a2 feat: 電流データクラスに不正値を弾くロジックを追加
    - 399fb02 feat: 電圧、電流用のデータクラス、テスト追加
    - 434a074 feat: 温度用のデータクラス、データクラスのテストを追加
- **所要時間**:1時間

## 実施内容
- /src/ci_playground/domain/readings.pyに温度、電圧、電流のデータクラスを追加
- /tests/unit/domainに温度、電圧、電流のデータクラス用のテストスクリプトを追加

## ポイント（学んだこと・選択の理由）
- @dataclassのデコレータを使用することで、自動で __eq__/__hash__/__repr__ を生成
- @dataclass(frozen=True) でデータクラスを不変にすることができる
- pytestで例外を想定する箇所は`with pytest.raises(ValueError):`の後に例外をスローする処理を書くことで試験として登録できる
- テストの関数は何をテストしているかがわかるように英文をスネークケースで接続して記載する（例：test_should_not_allow_value_modification）

## 詰まったところ
### 詰まり1: NaN シンボルが Python に存在しない
- **症状**: `CurrentReading(value=NaN)`で`F821 Undefined name 'NaN'`
- **原因**: JavaScriptと混同。Pythonには `Nan` 予約語がない
- **解決**: `float("nan")` で生成。 `math.isginite()` で NaN/±Inf 一括検査
- **学び**: 言語間でNaN表現は違う。Pythonでは「特別な float 値」として扱う

## 結果
- ドメイン層のデータクラスを定義し、ドメイン層のテストをCIに組み込むことができた

## 次の一歩
- Phase 3: DB仮想化