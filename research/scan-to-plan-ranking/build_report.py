# -*- coding: utf-8 -*-
"""Render the data half of report.html from candidates.json / studies.json."""
import json, html, re, collections

C = json.load(open('candidates.json'))
S = json.load(open('studies.json'))
e = lambda x: html.escape(str(x or ''), quote=True)

def dim(num, label):
    return (f'<div class="dim"><span class="num">{e(num)}</span>'
            f'<span class="line"><span class="cap"></span></span>'
            f'<span class="num">{e(label)}</span></div>')

# ---- curated shortlist: LiDAR + floor-plan/CAD output, relevant to estimate-grade use ----
SHORT = [
 # name, region, type, dxf, area takeoff, note
 ("Scanat（スキャナット）","日本","A/D","○ 間取りスキャンからDXF","計測値・面積をCSV書き出し","端末内でDXF生成。別途CAD作図代行あり。3D は FBX/OBJ/STL/E57/XYZ"),
 ("mapry建築","日本","A","○ ただし有料プラン","部屋別CSV","間取り図に加え立面図も自動生成。3D は USDZ/OBJ、点群 PLY/TXT。アプリ本体は無料"),
 ("間取りスキャナー","日本","A","○ JWCAD/AutoCAD へ出力","記載あり（要確認）","マプリィ×キャドネット。平面図・立面図・3Dパースを自動生成し Walk in home SP へ連携"),
 ("りのべっち","日本","A","△ ARCHITREND ZERO 経由","ZERO側で積算","福井コンピュータ。壁線スキャンで寸法付き現況間取り図。DXF直接出力は未確認"),
 ("Re:BIM","日本","B","△ 未確認","◎ 床壁天井の面積・数量から見積を自動作成","スターツ。退去修繕・リフォーム特化。iPad Pro LiDAR専用アプリ。用途①との適合度が高い"),
 ("リモデラメジャー","日本","A","△ 未確認","△ 未確認","REMODELA。RoomPlanベースの無料採寸・間取図アプリ。同社「だれでも現地調査」は見積書自動生成"),
 ("room me","日本","B","△ 未確認","記載あり（要確認）","TWPLAN。原状回復特化。スキャン→見積・工程・報告書・請求まで一元管理"),
 ("pronoScan2CAD","日本","C","○ 点群から2D DXF","なし","プロノハーツ。LiDAR点群から計測平面を抽出しDXF線図を出力。作図は別途"),
 ("magicplan","海外","A","○","面積・CSV書き出し","Sensopia。PDF/DXF/JPG/PNG/SVG/CSV/OBJ/USDZ/Xactimate ESX。復旧・見積業界で実績"),
 ("Polycam","海外","A","○ Business プラン限定","記載あり（要確認）","レイヤ分けDXF。PDF/SVG/PNG/CSV および点群・メッシュ多数。DXFはプラン制約に注意"),
 ("RoomScan Pro LiDAR","海外","A","○","△ 未確認","Locometric。PNG/PDF/DXF/IFC/点群。ドア・窓の認識あり。作図代行も提供"),
 ("Metaroom","海外","B","○","△ 未確認","AMRAX。パラメトリック3D室モデル＋2D間取り。DXF/PDF/IFC/GLB ほか30形式超。Archicad公式パートナー"),
 ("ArcSite","海外","A","○ DXF・DWG","△ 未確認","CAD作図アプリ内で編集可能。Android版あり"),
 ("Canvas / Twindo Scan to CAD","海外","D","○ 作図後CADで納品","作図物に依存","LiDARスキャンを送ると人がレイヤ分けCADを作図。$0.14/sqft〜、納期1〜2日（検索記録）"),
 ("CubiCasa","海外","D","△ DWG は明記、DXF未確認","寸法入り間取り","歩き回るだけのスキャン。24時間以内納品、6時間特急あり"),
 ("i3Dfolio / OpenPlan3D / RoomPlot / CamPlan","海外","A","○（各社ページ記載）","△ 未確認","いずれもLiDAR→編集可能な2D間取り＋DXF出力を掲げる小規模プロダクト。実在性と継続性の確認が必要"),
]

parts = []

# ---- 0. blocking notice ----
parts.append('''
<div class="notice">
  <p class="t"><span class="dot"></span>この調査は途中で止まっている。順位は確定していない</p>
  <p>本セッションの実行環境は外部ネットワークがアローリスト制で、GitHub 等以外への接続がすべて遮断されている。ベンダー公式サイト・App Store・学術出版社のページ本文は一切取得できなかった。</p>
  <p>したがって設計上の <b>立証フェーズ（一次情報の取得）</b>と<b>サンプルDXFの実ファイル回収</b>は実行できていない。以下に並ぶ製品情報は<b>検索インデックス由来の未取得情報</b>であり、本調査の規則では一次情報として採用できない。数値・価格・出力形式はいずれも発注判断の根拠にしてはならない。</p>
  <ul>
    <li>完了しているのは<b>発見フェーズのみ</b>（設計上、二次情報の使用が認められている工程）</li>
    <li>順位を決める実測（同一物件テスト）は人間・実機の作業であり未実施</li>
    <li>再開には、ベンダードメインへの接続を許可した環境が必要</li>
  </ul>
</div>''')

# ---- 1. method ----
parts.append(dim('01','判定方法'))
parts.append('''<div class="sec-head col"><h2>精度は足切り、順位は工数</h2>
<p>精度と手間を足し算して総合点を作らない。用途①（見積用）では点群のミリ精度は問わないため、必要精度を満たすかどうかで土俵に上げ、その中を実測した工数だけで並べる。重み付き総合点は重みの根拠が主観になり、結局「総合的に判断して1位」に戻るため採用しない。</p></div>''')
parts.append('''<div class="scroller"><table>
<thead><tr><th>区分</th><th>内容</th><th>状態</th></tr></thead><tbody>
<tr><td class="name">足切り 1</td><td>LiDAR を計測に使用（iPhone / iPad Pro で動作）</td><td><span class="pill hold">未検証</span></td></tr>
<tr><td class="name">足切り 2</td><td>DXF を出力できる（プラン名・追加費用の明記を含む）</td><td><span class="pill hold">未検証</span></td></tr>
<tr><td class="name">足切り 3</td><td>ひとりで完結（三脚・補助者・外部スキャナが必須でない）</td><td><span class="pill hold">未検証</span></td></tr>
<tr><td class="name">足切り 4</td><td>床面積誤差 ±3% 以内／主要寸法誤差 ±50mm 以内／再現性が同範囲</td><td><span class="pill hold">実測待ち</span></td></tr>
<tr><td class="name">主KPI</td><td>1戸あたり人的工数（分）＝ 撮影時間 ＋ 修正時間。待ち時間は加算せず別掲</td><td><span class="pill hold">実測待ち</span></td></tr>
</tbody></table></div>
<p class="note-s">用途①では図面そのものより<b>数量が自動で出るか</b>が工数を支配する。床面積・壁面積（開口部の控除が自動か）・天井面積・開口部の寸法拾い・数量表の書き出し形式を全製品の必須確認項目に置いている。</p>''')

# ---- 2. provenance legend ----
parts.append(dim('02','出典の種別'))
parts.append('''<div class="sec-head col"><h2>どの情報が、どの強さで裏づけられているか</h2>
<p>この調査の要は、ベンダーの主張を測定値として扱わないことにある。全データに種別を付し、種別の混在を画面上で見えるようにしている。</p></div>''')
parts.append('''<div class="legend">
<div><span class="chip measured">実測</span><p>同一物件テストで自分が測った値。順位を決めてよい唯一の情報。<b>現時点で0件。</b></p></div>
<div><span class="chip store">ストア構造化</span><p>App Store の互換性欄・最終更新日・価格など。事実として扱える。<b>取得できず0件。</b></p></div>
<div><span class="chip artifact">実ファイル</span><p>ベンダー公開のサンプルDXF/PDFを実際に開いて確認した所見。<b>取得できず0件。</b></p></div>
<div><span class="chip thirdparty">第三者検証</span><p>測定条件と数値がある学術・公的検証。<b>書誌のみ8件、本文は未取得。</b></p></div>
<div><span class="chip vendor">ベンダー主張</span><p>公式ページの記述。事実ではなく主張として記録する。<b>本文未取得のため0件。</b></p></div>
<div><span class="chip search">検索由来</span><p>検索インデックスのタイトルとスニペット。本調査の規則では評価に使えない。<b>本ページの製品情報はすべてこれ。</b></p></div>
</div>''')

# ---- 3. population ----
byt = collections.Counter(c.get('type') for c in C)
jp = sum(1 for c in C if re.search(r'[぀-ヿ一-鿿]', c.get('vendor','')))
lid = sum(1 for c in C if c.get('lidar')=='yes')
dxf = sum(1 for c in C if 'DXF' in (c.get('note','') or '').upper())
parts.append(dim('03','母集団'))
parts.append('''<div class="sec-head col"><h2>117 製品を4つの出力形態に分類した</h2>
<p>単体アプリだけを見ると選択肢を落とす。業務システム内蔵の現調機能、点群止まりのツール、そして人が作図する代行サービスまでを同じ母集団に入れている。「手間なく」を基準にすると、D型（代行）が最短になる場合がある。</p></div>''')
parts.append(f'''<div class="stats">
<div><span class="n">{len(C)}</span><span class="l">名寄せ後の製品数</span></div>
<div><span class="n">{jp}</span><span class="l">日本ベンダー</span></div>
<div><span class="n">{lid}</span><span class="l">LiDAR 対応と記載</span></div>
<div><span class="n">{dxf}</span><span class="l">DXF に言及</span></div>
</div>''')
parts.append(f'''<div class="scroller"><table>
<thead><tr><th>型</th><th>中身</th><th class="num">件数</th><th>この用途での位置づけ</th></tr></thead><tbody>
<tr><td class="name">A</td><td>端末内で自動作図、その場で平面図</td><td class="num">{byt.get('A',0)}</td><td>本命。修正工数で差がつく</td></tr>
<tr><td class="name">B</td><td>クラウド処理 → 図面が返る</td><td class="num">{byt.get('B',0)}</td><td>本命。待ち時間と単価を別掲</td></tr>
<tr><td class="name">C</td><td>点群・メッシュ止まり、作図はCADで人が行う</td><td class="num">{byt.get('C',0)}</td><td>参考枠。図面工数が丸ごと残る</td></tr>
<tr><td class="name">D</td><td>スキャン送付 → 人が作図して納品</td><td class="num">{byt.get('D',0)}</td><td>手間の少なさでは有力</td></tr>
<tr><td class="name">未分類</td><td>出力形態を確認できていない</td><td class="num">{byt.get('unknown',0)}</td><td>立証フェーズで分類する</td></tr>
</tbody></table></div>''')

# full list
rows=[]
for c in sorted(C, key=lambda x:(0 if re.search(r'[぀-ヿ一-鿿]',x.get('vendor','')) else 1, x['product'])):
    jpv = '日本' if re.search(r'[぀-ヿ一-鿿]', c.get('vendor','')) else '海外'
    li = {'yes':'<span class="yes">○</span>','no':'<span class="no">×</span>'}.get(c.get('lidar'),'<span class="na">—</span>')
    rows.append(f'<tr><td class="name">{e(c["product"])}<span class="vendor">{e(c.get("vendor"))}</span></td>'
                f'<td class="num">{e(jpv)}</td><td class="num">{e(c.get("type"))}</td><td class="num">{li}</td>'
                f'<td>{e(c.get("note"))[:180]}</td></tr>')
parts.append(f'''<details class="more"><summary>母集団 {len(C)} 件をすべて表示</summary>
<div class="scroller" style="border:none;box-shadow:none;border-radius:0"><table>
<thead><tr><th>製品 / 提供元</th><th class="num">地域</th><th class="num">型</th><th class="num">LiDAR</th><th>発見時の記載（検索由来・未検証）</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div></details>''')

# ---- 4. shortlist ----
parts.append(dim('04','検証候補'))
parts.append('''<div class="sec-head col"><h2>次に立証すべき16の候補</h2>
<p>LiDAR を使い、間取り図または CAD 納品まで到達し、ひとりで運用できそうなものを抜き出した。<b>これは順位ではない</b>。各セルの記載はすべて検索由来であり、次工程で公式ページと実ファイルにあたって確定させる対象を示している。</p></div>''')
srows=[]
for i,(n,reg,ty,dx,ar,nt) in enumerate(SHORT,1):
    srows.append(f'<tr><td class="num rank">{i:02d}</td><td class="name">{e(n)}</td>'
                 f'<td class="num">{e(reg)}</td><td class="num">{e(ty)}</td>'
                 f'<td>{e(dx)}<br><span class="chip search">検索由来</span></td>'
                 f'<td>{e(ar)}<br><span class="chip search">検索由来</span></td><td>{e(nt)}</td></tr>')
parts.append(f'''<div class="scroller"><table>
<thead><tr><th class="num">#</th><th>製品</th><th class="num">地域</th><th class="num">型</th><th>DXF 出力</th><th>面積の自動算出</th><th>備考</th></tr></thead>
<tbody>{''.join(srows)}</tbody></table></div>
<p class="note-s">番号は掲載順であり優劣ではない。用途①（見積用）との適合という観点では、面積・数量が自動で出ると記載のあるもの — Re:BIM、magicplan、Scanat、mapry建築 — が優先的な検証対象になる。</p>''')

# ---- 5. studies ----
parts.append(dim('05','精度の第三者検証'))
parts.append('''<div class="sec-head col"><h2>Apple LiDAR の精度を実測した文献</h2>
<p>採否の基準は一行、<b>測定条件と数値が書いてあるか</b>。レビュー記事は除外している。ただし本文が取得できていないため、以下はいずれも書誌情報と検索記録の段階にとどまる。引用の前に本文を読むこと。</p></div>''')
trows=[]
for s in S:
    warn = ' <span class="chip unknown">要再確認</span>' if 'LOW_CONFIDENCE' in s.get('verified','') else ''
    trows.append(f'<tr><td class="name" style="white-space:normal;max-width:24em">{e(s["title"])}'
                 f'<span class="vendor">{e(s.get("authors"))}{" / "+str(s["year"]) if s.get("year") else ""} · {e(s.get("venue"))}</span></td>'
                 f'<td>{e(s.get("reference_instrument"))}</td><td>{e(s.get("reported_error"))}{warn}</td>'
                 f'<td>{e(s.get("conditions"))}</td></tr>')
parts.append(f'''<div class="scroller"><table>
<thead><tr><th>文献</th><th>基準器</th><th>報告された誤差</th><th>測定条件</th></tr></thead>
<tbody>{''.join(trows)}</tbody></table></div>
<p class="note-s">屋内・室スケールでトータルステーションや地上型レーザースキャナと直接比較したものが、この用途には最も近い。屋外や地形を対象にした文献は参考にとどめる。用途①の足切り（床面積±3%、主要寸法±50mm）に照らすと、これらの報告値は概ね桁として足りているが、確認は自前の実測で行う。</p>''')

# ---- 6. worklist ----
parts.append(dim('06','再開手順'))
parts.append('''<div class="sec-head col"><h2>この続きに必要なこと</h2>
<p>設計・スキーマ・採点規則・実測プロトコルは確定済みで、リポジトリに収録してある。止まっているのはデータ取得だけなので、接続さえ通れば同じ手順をそのまま再実行できる。</p></div>''')
parts.append('''<div class="wl">
<div><h3>ネットワークの解放</h3><p>ベンダードメイン・App Store・学術出版社への接続を許可した環境で再実行する。現状は GitHub 等のみのアローリストで、これが唯一の障害になっている。</p></div>
<div><h3>立証フェーズ</h3><p>16候補それぞれに1担当を割り当て、共通スキーマの全項目を出典URL・引用・取得日つきで埋める。価格体系と DXF の可否は Pricing ページの脚注とヘルプセンターにしか無いことが多い。</p></div>
<div><h3>実ファイルの回収</h3><p>サンプル DXF を実際にダウンロードして CAD で開く。壁の閉合、レイヤ分け、寸法の有無、日本語の文字化け、単位が mm か。ここで初めて「図面精度」が主張から事実になる。</p></div>
<div><h3>反証</h3><p>順位を動かす3点だけを崩しにいく。DXF が本当にどのプランで出るか、面積の壁面積控除が本当に自動か、スキャン単価や㎡単価が隠れていないか。</p></div>
<div><h3>同一物件テスト</h3><p>正解寸法を先に確定し、現場担当者本人が、補助者・三脚なし、家具を動かさずに全候補を通す。2回スキャンして再現性を見る。機内モードで1回。</p></div>
<div><h3>順位の確定</h3><p>足切りを通過したものを、撮影時間＋修正時間の実測値の昇順に並べる。それ以外の情報は併記列に置き、トレードオフは読み手に見せる。</p></div>
</div>''')

s = open('report.html').read()
s = s.replace('<!--DATA-->', '\n'.join(parts))
open('report.html','w').write(s)
print('report.html rendered:', len(s), 'bytes')
