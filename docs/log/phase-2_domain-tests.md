# Phase 2: ドメイン層データクラス定義とテスト

- **日付**: 2026-06-07, 2026-06-08, 2026-06-09
- **関連コミット/PR**:
    - e90131d feat(ci): カバレッジをCIに追加
    - 203d00f feat(domain): Device集約ルートとテストを追加
    - 45f289a docs(log): Phase 2-5 の内容をログに追記
    - 9526040 fix(domain): 追加部分のruff format
    - 3aa6169 feat(domain): Sensorエンティティとテストを追加
    - dfdafaa feat(domain): SensorType, Range, SensorId, DeviceIdとテストを追加
    - 37ea8ce docs(log): Phase 2 のログを修正、次のステップを変更
    - 5a30691 docs(log): Phase 2 のログの誤記修正、詰まりポイント追加
    - 9b46074 docs(log): Phase 2 ログを作成
    - 16c4e2f feat(test): 電流データクラスに対する無限大、NaN例外テスト追加
    - 1b6b1aa fix(domain): 電流データクラスのmathインポート忘れ対応
    - eacb6a2 feat: 電流データクラスに不正値を弾くロジックを追加
    - 399fb02 feat: 電圧、電流用のデータクラス、テスト追加
    - 434a074 feat: 温度用のデータクラス、データクラスのテストを追加
- **所要時間**:5時間

## 実施内容
- /src/ci_playground/domain/readings.pyに温度、電圧、電流のデータクラスを追加
- /tests/unit/domainに温度、電圧、電流のデータクラス用のテストスクリプトを追加
- /src/ci_playground/domain/values.pyにRange、SensorId, DeviceIdのデータクラスを追加
- /src/ci_playground/domain/values.pyにSensorTypeの文字列列挙型を追加
- /tests/unit/domainにvalues.pyのテストスクリプトを追加
- /src/ci_playground/domain/sensor.pyにSensorエンティティを追加
- /tests/unit/domainにsensor.pyのテストスクリプトを追加
- /src/ci_playground/domain/device.pyにDevice集約ルートを追加
- /tests/unit/domainにdevice.pyのテストスクリプトを追加
- CIにカバレッジを追加 `run: uv run pytest --cov --cov-report=term-missing`

## ポイント（学んだこと・選択の理由）
- @dataclassのデコレータを使用することで、自動で __eq__/__hash__/__repr__ を生成
- @dataclass(frozen=True) でデータクラスを不変にすることができる
- pytestで例外を想定する箇所は`with pytest.raises(ValueError):`の後に例外をスローする処理を書くことで試験として登録できる
- テストの関数は何をテストしているかがわかるように英文をスネークケースで接続して記載する（例：test_should_not_allow_value_modification）
- 真偽値を返す関数の場合は、真のとき：assert (関数)、偽のとき：assert not (関数) で良い。(== trueは冗長のためruffに指摘される)
- .strip()で文字列から空白を除去して、空文字判定を楽に行うことができる
- EnumのメンバアクセスはSensorType.TEMPERATUREのようにメソッドのように呼び出すことができる
- @dataclass(eq=False) で__init__は自動生成し、自前 __eq__ を追加することができる
- @dataclass(eq=False) を選んだ理由：自動生成の __eq__（全フィールド比較）はエンティティのID等価と矛盾するため、eq=False で生成抑制 → 自前の ID ベース __eq__ を書く
- __eq__ と __hash__ の整合性契約：「a == b なら hash(a) == hash(b)」が Python のハッシュ可能オブジェクトの絶対条件、IDベース等価ならハッシュもID由来
- @property化することでメソッドを呼び出すときに()不要となる（例：s.is_anomalous）
- == None ではなく is None と書く（PEP8）
- `--cov --cov-report=term-missing` でCIにカバレッジを追加してGitHub画面で結果が確認できる
- `--cov-fail-under=90` でカバレッジが90%を下回ったらCI失敗にする制約を加えることができる
- カバレッジは100%を必ず追う必要はない。特に例外など発生する可能性が低いところまですべてカバーする意味は薄い。


## 詰まったところ
### 詰まり1: NaN シンボルが Python に存在しない
- **症状**: `CurrentReading(value=NaN)`で`F821 Undefined name 'NaN'`
- **原因**: JavaScriptと混同。Pythonには `NaN` 予約語がない
- **解決**: `float("nan")` で生成。 `math.isfinite()` で NaN/±Inf 一括検査
- **学び**: 言語間でNaN表現は違う。Pythonでは「特別な float 値」として扱う

### 詰まり2: dataclass import 忘れ＋自分の self. 忘れの繰り返し
- 症状: NameError: dataclass is not defined、NameError: min is not defined
- 原因: import文の追加忘れ、__post_init__ 内で self.min を min と書いてしまう
- 学び: ruff check で F821 として早期検出できる

### 詰まり3: min, max: float で min が dataclass フィールドにならない罠
- 症状: @dataclass が min を未注釈と判断、フィールドとして認識しない
- 原因: min, max: float という多重名アノテーションは max のみに型を付ける
- 学び: 各属性ごとに1行で min: float / max: float と書くべき

### 詰まり4: 組み込み range() と自作 Range の名前衝突
- 症状: テストで range(min=10.0, max=20.0) と書いてしまい、組み込み関数として実行され、キーワード引数で TypeError
- 原因: クラスを小文字で参照、大文字小文字を区別せず混同
- 学び: クラス名は PascalCase、組み込みと衝突しないか意識する

### 詰まり5: () 抜けの false positive（Phase 2 最大の学び）
- 症状: assert s.is_anomalous が実装が壊れていても緑になる
- 原因: メソッドを呼ばずに参照しているだけ、メソッドオブジェクトは truthy
- 解決: () を付ける、または @property 化
- 学び: テストの信頼性自体が損なわれる、@property という選択肢を知った

### 詰まり6: record() の判定ロジックが逆転（ネスト if の罠）
- 症状: 型一致しているのに毎回 ValueError
- 原因: if isinstance(reading, expected): if reading != expected: という二重ifで、内側が常に True
- 解決: ガード節パターン（だめな条件を最初に raise、残ったら本流処理）
- 学び: 早期 return/raise でネストを浅く保つ Pythonic

### 詰まり7: テストメソッドの同名重複で1つが消えた
- 症状: 2つ目の test_should_not_be_anomalous_when_within_range が1つ目を上書き
- 原因: Python は同名メソッドを後勝ち、ruff F811 で検出
- 学び: テスト名は仕様を表す、コピペ時に名前を変える習慣

### 詰まり8: assert s == r で s, r が未定義
- 症状: NameError
- 原因: if isinstance(reading, expected): if reading != expected: という二重ifで、内側が常に True
- 解決: ガード節パターン（だめな条件を最初に raise、残ったら本流処理）
- 学び: 早期 return/raise でネストを浅く保つ Pythonic

### 詰まり7: テストメソッドの同名重複で1つが消えた
- 症状: 2つ目の test_should_not_be_anomalous_when_within_range が1つ目を上書き
- 原因: Python は同名メソッドを後勝ち、ruff F811 で検出
- 学び: テスト名は仕様を表す、コピペ時に名前を変える習慣

### 詰まり8: assert s == r で s, r が未定義
- 症状: NameError
- 原因: 別テストからのコピペで変数名が残ったまま
- 学び: テストもリファクタが必要、テストコードの命名も丁寧に

### 詰まり9: Device(id=DeviceId("dev-01")) で DeviceId 未定義
- 症状: NameError
- 原因: test_device.py に import を追加し忘れた
- 学び: ruff check で F821 早期検出

### 詰まり10: if 文末尾のコロン抜け
- 症状: SyntaxError: expected ':'
- 原因: if any(...) のコロンを書き忘れ
- 学び: Python は if/for/while/def/class 後ろに必ず :、エラーメッセージが教えてくれる

## 結果
- ドメイン層の値オブジェクト（Reading系3種、SensorType, Range, SensorId, DeviceId）を実装
- エンティティ（Sensor）と集約ルート（Device）を実装し、DDD のID識別・状態管理・不変条件の表現を体感
- ドメイン層テスト62件、カバレッジ TOTAL 96%（domain層92-100%）を達成
- CIに `--cov --cov-report=term-missing` を組み込み、品質指標がGitHub上で見える状態にした

## 次の一歩
 - Phase 2 完了に伴い、Phase 3-A（DB仮想化）に進む
 - 並行して docstring CI 取り込み（Task #31）も実施