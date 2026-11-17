# 曖昧・不明なことリスト

## Q1. Lv70対応の仕様

<div class="form-item-body">
<div class="p-form-range">
<input type="range" id="levelSlider" min="0" max="3" step="1" value="2">
</div>
<div class="form-item-text">
<div class="showLevel">
<span>Lv. </span>
<input type="text" name="pokemon_level" id="levelDisplay" value="60" min="30" max="70">
</div>
</div>
</div>

まずここでレベルを70にします


<div class="form-item-select">
<div class="p-form-select">
<select name="pokemon_subskill4" id="subSkill4" class="select2-pokemon-container pokemon-subskill-array4 select2-hidden-accessible" tabindex="-1" aria-hidden="true" data-select2-id="subSkill4">
<option data-select2-id="315"></option>
<optgroup label="金スキル"><option value="11">げんき回復ボーナス</option><option value="12">ゆめのかけらボーナス</option><option value="13">リサーチEXPボーナス</option><option value="14">睡眠EXPボーナス</option><option value="15">おてつだいボーナス</option><option value="16">きのみの数S</option><option value="17">スキルレベルアップM</option></optgroup><optgroup label="青スキル"><option value="21">スキル確率アップM</option><option value="22">食材確率アップM</option><option value="23">スキルレベルアップS</option><option value="24">最大所持数アップL</option><option value="25">最大所持数アップM</option><option value="26">おてつだいスピードM</option></optgroup><optgroup label="白スキル"><option value="31">スキル確率アップS</option><option value="32">食材確率アップS</option><option value="33">最大所持数アップS</option><option value="34">おてつだいスピードS</option></optgroup></select><span class="select2 select2-container select2-container--default select2-container--focus" dir="ltr" data-select2-id="314" style="width: 570px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-disabled="false" aria-labelledby="select2-subSkill4-container"><span class="select2-selection__rendered" id="select2-subSkill4-container" role="textbox" aria-readonly="true"><span class="select2-selection__placeholder">Lv.70サブスキルを選択してください</span></span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span>
</div>
</div>

するとここのドロップダウンが押せるようになりLv70の調査が可能になります

## Q2. 再調査の優先順位と上限

元は登録日はあれど更新日がないんですよね
全体のjsonファイルを毎回ダウンロードする仕組みで運用しており
余りサイズを増やしたくないので更新日データは少ない方が良いです

upd:yymmddで短く管理するようにしてください
更新日の古い順に再調査を行います

最初はdcがないデータから新しい順で行います

**10件/日** をデフォルトで分かりやすく変更できるようにしてください

## Q3. データ移行方針

- **A案:** `new_d` はそのまま残し、新しく `dc` フィールドを追加する（互換性重視）

## Q4. `replaceUnknown` とサブスキル名の違い

これは **サイト側の相違に対応したため**です


## Q5. 実行モード（headless / GUI）

デフォルトはheadlessでお願いします

## Q6. 食材選択 `ingredients0` の扱い

本来一つ目の食材を変更できる特殊なポケモンが実装されているのですが
だいふく氏のサイトでは怠慢で固定化されています
将来的に使用する可能性があります

## Q7. `evolution.json` の更新

よくわかりませんがこのプロジェクトは既存から抜き出したものです
実際は最新データが使用されます

## Q8. Firebase連携の将来性

daifuku_req_test.py(追加)
daifuku_firebase_new.py
daifuku_firebase_food.py
firebaseImport.py(追加)

実際はこれらのファイルを順次実行していました

まとめたかったのですが
スクレイピングエラーの際毎回firebaseリクエストしてダウンロード量を使用してしまうため
分けています

今回の
daifuku_firebase_new.py
daifuku_firebase_food.py
の統合では必要ありません

## Q9. viewer（React）側の対応タイミング

しばらくは
daifuku_firebase_new.py
daifuku_firebase_food.py
も動かします

そして
このプロジェクトが完結してからreactの改修をすすめます

## Q10. 旧ファイルの扱い

プロジェクトから浮き取ったファイルなので要らないですが
改修の参考資料として保管した方が良いのではないかと思いますよ

## Q11. その他のサイト追加イメージ

他のサイトではないです、サイト内で改修が必要な場合
自分でもスクレイピングの動きを確認するため
人間でもわかるコメントや流れをイメージできるような設計思想でお願いします