# -*- coding: utf-8 -*-
"""Render report.html from the evidence files."""
import json, html, re, collections

C = json.load(open('candidates.json'))
S = json.load(open('studies.json'))
e = lambda x: html.escape(str(x if x is not None else ''), quote=True)
SEARCH = '<span class="chip search">検索由来</span>'

def dim(n, label):
    return (f'<div class="dim"><span class="num">{e(n)}</span>'
            f'<span class="line"><span class="cap"></span></span>'
            f'<span class="num">{e(label)}</span></div>')
def head(h, p):
    return f'<div class="sec-head col"><h2>{h}</h2><p>{p}</p></div>'

P = []

# ── notice ────────────────────────────────────────────────────────────
P.append('''<div class="notice">
<p class="t"><span class="dot"></span>順位は確定していない。以下は検索由来の情報である</p>
<p>本セッションの実行環境は外部ネットワークがアローリスト制で、ベンダー公式サイト・App Store・学術出版社への接続がすべて遮断されている。<b>ページ本文は一度も取得できていない。</b>以下の製品情報はすべて検索インデックスのスニペット由来であり、本調査の規則では一次情報として採用できない。</p>
<p>特に価格は、ディレクトリサイト間で系統的に矛盾している。Metaroom と ArcSite は4系統の異なる価格が並立し、magicplan も案件課金と月額課金の記述が併存する。<b>ここに載る金額を発注判断に使ってはならない。</b></p>
<p>順位を決める同一物件テスト（実測）も未実施。以下は「次に何を確認すべきか」を示すものである。</p>
</div>''')

# ── method ────────────────────────────────────────────────────────────
P.append(dim('01','判定方法'))
P.append(head('精度は足切り、順位は工数',
 '精度と手間を足し算して総合点を作らない。用途①（見積用）では点群のミリ精度は問わないため、必要精度を満たすかで土俵に上げ、その中を実測した工数だけで並べる。重み付き総合点は重みの根拠が主観になり、結局「総合的に判断して1位」に戻るため採用しない。'))
P.append('''<div class="scroller"><table>
<thead><tr><th>区分</th><th>内容</th><th>状態</th></tr></thead><tbody>
<tr><td class="name">足切り 1</td><td>LiDAR を計測に使用（iPhone / iPad Pro で動作）</td><td><span class="pill ok">概ね確認</span></td></tr>
<tr><td class="name">足切り 2</td><td>DXF を出力できる（プラン名・追加費用の明記を含む）</td><td><span class="pill hold">プラン未確定</span></td></tr>
<tr><td class="name">足切り 3</td><td>ひとりで完結（三脚・補助者・外部スキャナが必須でない）</td><td><span class="pill hold">大半が未記載</span></td></tr>
<tr><td class="name">足切り 4</td><td>床面積誤差 ±3% 以内／主要寸法誤差 ±50mm 以内／再現性が同範囲</td><td><span class="pill hold">実測待ち</span></td></tr>
<tr><td class="name">主KPI</td><td>1戸あたり人的工数（分）＝ 撮影時間 ＋ 修正時間。待ち時間は加算せず別掲</td><td><span class="pill hold">実測待ち</span></td></tr>
</tbody></table></div>''')

# ── the finding ───────────────────────────────────────────────────────
P.append(dim('02','用途①の核心'))
P.append(head('「DXFが出る」と「面積が自動で出る」は両立していない',
 '見積用途で工数を支配するのは図面ではなく数量である。そこで全製品について、床面積だけでなく<b>壁面積</b>（クロス）・天井面積・<b>開口部の自動控除</b>・数量表の書き出しを確認した。結果、この2つが揃う製品はごく少ない。'))
AREA = [
 ("magicplan","海外","○ 寸法なし","床・周長・居住面積、壁面積を総面積と正味面積の2種","○ 唯一明示","PDF / CSV","開口部控除を明示している唯一の製品。ただしDXFに寸法が入らないと公式ヘルプに明記"),
 ("Metaroom","海外","○ 2D/3D","室名・面積m²・体積m³・天井高・壁長・壁面積","記載なし","Excel / PDF","Excelに直接出力、手入力不要と明記。第三者裏付けが最も厚い"),
 ("ArcSite","海外","○ Draw Pro以上","作図ジオメトリから材料拾いを自動生成、壁・天井の形状に対応","アプリ本体では未確認","PDF / Excel / CSV","材料拾いが製品の中核。ただしCAD読込は非対応"),
 ("RoomScan Pro","海外","○","天井高を自動計測し壁面積を算出、熱損失も","記載なし","記載なし","DXFへの到達コストが最も低い。CSV数量出力は確認できず"),
 ("Polycam","海外","△ プラン矛盾","室別面積・壁寸法・窓面積・什器寸法","記載なし（窓面積は別項目）","CSV / PDF","日本語UIが確認できた唯一の海外製品。オフラインも明確"),
 ("mapry建築","日本","○ 月額900円","各部屋と外皮（窓を含む）の寸法","記載なし","CSV","DXFへの到達が月900円と突出して安い。平面図に加え立面図も出力"),
 ("Scanat","日本","○ 端末内即時","2点で距離、3点以上で面積、天井高","記載なし","CSV","オフライン可・1人運用可が明記。ただし1ID月12,000円"),
 ("間取りスキャナー","日本","○ JWCAD/AutoCAD","面積や開口部などの数量を書き出し、積算・見積まで一貫","開口部の数量に言及","記載あり","記述は用途①に最も近い。ただし料金が公開情報に一切なし"),
 ("Re:BIM","日本","記載なし","床・壁・天井の面積と設備・建具の数量から見積を自動作成","記載なし","見積書","面積→見積の自動化は最も進む。60-70m²で計約30分。DXFの記載なし・価格非公開・iPad Pro専用"),
 ("OpenPlan3D","海外","○ 無料","室面積のみ","なし","記載なし","DXFが無料で出せる唯一。ただし壁面積が出ず見積用途では機能不足"),
 ("RoomPlot","海外","○ 有料","室面積のみ","なし","記載なし","$29.99/年と安価。面積は室面積のみ"),
 ("pronoScan2CAD","日本","○ 年6,000円","なし（点群上で手作業で線を引く）","なし","なし","DXFは確実だが自動作図も面積もない。用途文脈は土木・測量寄り"),
]
rows=''.join(
 f'<tr><td class="name">{e(n)}</td><td class="num">{e(r)}</td><td>{e(d)}</td><td>{e(a)}</td>'
 f'<td>{e(o)}</td><td class="num">{e(q)}</td><td>{e(nt)}</td></tr>'
 for n,r,d,a,o,q,nt in AREA)
P.append(f'''<div class="scroller"><table>
<thead><tr><th>製品</th><th class="num">地域</th><th>DXF</th><th>面積の算出範囲</th><th>開口部控除</th><th class="num">数量出力</th><th>所見</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="note-s">{SEARCH} 全セルが検索スニペット由来。<b>開口部控除を明示しているのは magicplan のみ</b>で、残りは「記載がない」だけであり無いとは限らない。壁面積まで出せるのは magicplan / Metaroom / ArcSite / RoomScan の4製品。</p>''')

P.append('''<div class="banner">
<p class="t"><span class="dot"></span>足切り条件そのものを見直す余地がある</p>
<p>日本製品では、面積→見積を自動化する Re:BIM・room me・だれでも現地調査 のいずれにも DXF 出力の記載がなく、DXF が確実な pronoScan2CAD には面積算出も自動作図もない。DXF を必須にすると、数量が自動で出る日本製品が全滅する可能性がある。</p>
<p>見積用途で本当に必要なのは数量であって図面ファイルではない。DXF を足切りから外し「CADに渡せること」を任意条件に降格させるほうが、実務に合う結果になるかもしれない。この判断は発注者の運用次第なので、決めていただきたい。</p>
</div>''')

# ── formats matrix ────────────────────────────────────────────────────
P.append(dim('03','出力形式'))
P.append(head('製品 × 出力形式',
 'ご要望の「出力可能な形式を知りたい」に対応する。括弧内は解放条件。空欄は記載が見つからなかったもので、非対応とは限らない。'))
FMT=[
 ("magicplan","○（寸法なし）","","PDF/JPG/PNG/SVG","CSV","OBJ / USDZ / IFC","Xactimate ESX, CoreLogic FML"),
 ("Polycam","○（プラン矛盾）","","PDF/PNG/SVG","CSV","OBJ/FBX/DAE/USDZ/STL/GLTF","点群 PLY/LAS/PTS/XYZ"),
 ("RoomScan Pro","○（サブスク）","","PNG/PDF","","OBJ/PLY/XYZ / IFC","FML, Xactimate ESX, Sweet Home 3D, RapidSketch, Metropix"),
 ("Metaroom","○ 2D/3D","","PDF/PNG/SVG","Excel XLS","FBX/ABC/DAE/GLTF/GLB/STL/OBJ/USD","IFC 2x3・v4 ほか各CAD向けIFC、MP4"),
 ("ArcSite","○（Draw Pro）","○ DWG","PDF/PNG","Excel/CSV","","CAD読込は非対応"),
 ("CamPlan","○（Pro $20/月）","","PDF/PNG/SVG","CSV/JSON","USDZ/OBJ/DAE",""),
 ("OpenPlan3D","○ 無料","","PDF/PNG/SVG","","USDZ","MITライセンス・GitHub公開"),
 ("RoomPlot","○（有料）","","PDF/PNG/JPG","","USDZ","複数ページのブランド付きPDFレポート"),
 ("mapry建築","○（月900円）","","","CSV（部屋・外皮）","USDZ/OBJ","点群 PLY/TXT。平面図に加え立面図もDXF"),
 ("Scanat","○ 端末内","","","CSV（寸法・面積）","FBX/OBJ/STL","点群 E57/XYZ。別途CAD作図代行 2-4営業日"),
 ("間取りスキャナー","○","○ AutoCAD","","記載あり","","JWCAD、Walk in home SP へ変換"),
 ("りのべっち","記載なし","","PDF（調査報告書）","","","ARCHITREND ZERO へ自動変換"),
 ("pronoScan2CAD","○（年6,000円）","","","","","2次元CADのみ"),
]
frows=''.join(f'<tr><td class="name">{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td><td>{e(d)}</td><td>{e(f)}</td><td>{e(g)}</td><td>{e(h)}</td></tr>' for a,b,c,d,f,g,h in FMT)
P.append(f'''<div class="scroller"><table>
<thead><tr><th>製品</th><th>DXF</th><th>DWG</th><th>画像・PDF</th><th>数量</th><th>3D</th><th>その他</th></tr></thead>
<tbody>{frows}</tbody></table></div>
<p class="note-s">{SEARCH} DXF が無料で出せるのは OpenPlan3D のみ。日本製では mapry建築 の月額900円が最安の到達路。</p>''')

# ── device / offline / japan ──────────────────────────────────────────
P.append(dim('04','運用条件'))
P.append(head('端末・オフライン・日本語',
 '現場はひとりスキャンで LiDAR 前提という条件に対し、実運用を左右する3点を並べた。電波が入らない現場があるならオフラインは足切りに近い重みを持つ。'))
OPS=[
 ("magicplan","iPhone 12 Pro以降 / iPad Pro、iOS17以降","不明（案件閲覧のみ言及）","日本語UIなし","Androidはスキャン不可・手入力のみ"),
 ("Polycam","iPhone 12 Pro以降 / iPad Pro 2020以降、iOS18以降","○ 明記","○ 日本語UIあり","請求書・電信送金はEnterpriseのみ"),
 ("RoomScan Pro","iPhone 12 Pro〜17 Pro / iPad Pro 2020以降","△ 出典が弱い","未確認","非LiDAR機向けTouch Mode、Bosch/Leica距離計対応"),
 ("Metaroom","iPhone 12 Pro以降 / iPad Pro 2020以降","◎ 機内モードでも可","未確認","出力はクラウド側。3Dモデル閲覧にアップロードが必要"),
 ("ArcSite","アプリはiOS/Android/Windows。ARスキャンはApple Pro機のみ","○ 明記","未確認","2000sqft超は複数スキャンを結合"),
 ("mapry建築","LiDAR搭載 iPhone Pro必須、iPhone 12 Pro〜15 Pro Max","○ DXF出力もネットワーク不要","日本製","ひとり運用の記載なし"),
 ("Scanat","LiDAR搭載 iPhone Pro / iPad Pro","○ 明記","日本製","端末1台・担当者1人で運用可能と明記"),
 ("Re:BIM","iPad Pro 第3世代以降 専用アプリ","未確認","日本製","iPhone対応の記載がなく、iPhone前提の運用と噛み合わない可能性"),
 ("room me","iPhone 12/13/14/15 Pro、iPad Pro 2020以降","未確認","日本製","1人で現場調査と明記。原状回復に業種限定"),
 ("りのべっち","3DスキャンはiPhone 12 Pro以上 / iPad Pro、iOS16以降","未確認","日本製","アプリ無償だがZERO連携に別途契約が必要"),
]
orows=''.join(f'<tr><td class="name">{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td><td>{e(d)}</td><td>{e(f)}</td></tr>' for a,b,c,d,f in OPS)
P.append(f'''<div class="scroller"><table>
<thead><tr><th>製品</th><th>端末要件</th><th>オフライン</th><th>日本語</th><th>備考</th></tr></thead>
<tbody>{orows}</tbody></table></div>
<p class="note-s">{SEARCH} <b>全製品が iPhone 12 Pro 以降の Pro 系を要求する。</b>LiDAR スキャンを Android で提供する製品は本調査の範囲に存在しない。ひとり運用を明記しているのは Scanat と room me のみで、他は否定もされていない。</p>''')

# ── outsourcing ───────────────────────────────────────────────────────
P.append(dim('05','外注との比較'))
P.append(head('自社スキャンは、外注より安くなければ意味がない',
 '「手間なく図面」を突き詰めると、人に作図させる選択肢が最短になり得る。そこで日本の作図代行の相場を押さえ、自社スキャン導入の損益分岐を見えるようにした。'))
P.append(f'''<div class="scroller"><table>
<thead><tr><th>ルート</th><th class="num">価格</th><th class="num">納期</th><th>DXF</th><th>入力</th><th>日本から発注</th></tr></thead><tbody>
<tr><td class="name">日本の図面トレース代行</td><td class="num">7,000〜15,000円/枚</td><td class="num">3〜5営業日</td><td class="yes">○ 標準</td><td>紙・PDF・手描きの<b>既存図面</b></td><td class="yes">○</td></tr>
<tr><td class="name">日本の平面図 原図起こし</td><td class="num">15,000〜50,000円/枚</td><td class="num">3〜5営業日</td><td class="yes">○ 標準</td><td>既存図面</td><td class="yes">○</td></tr>
<tr><td class="name">Canvas / Twindo Scan to CAD</td><td class="num">$0.14〜0.18/sqft</td><td class="num">約2営業日</td><td class="na">明示なし（DWG納品）</td><td><b>自社アプリのスキャンのみ</b></td><td class="na">不明</td></tr>
<tr><td class="name">CubiCasa</td><td class="num">CAD追加 $50</td><td class="num">24時間 / 特急6時間</td><td class="na">明示なし（DWG納品）</td><td>スマホスキャン</td><td class="na">不明・室名に日本語なし</td></tr>
<tr><td class="name">MP2FP</td><td class="num">公開価格なし</td><td class="num">不明</td><td class="yes">○ 明示</td><td>任意の点群・OBJ・MatterPak</td><td class="na">不明</td></tr>
<tr><td class="name">広告用間取り図代行</td><td class="num">180〜630円/件</td><td class="num">当日〜翌日</td><td class="no">×</td><td>既存スケッチ</td><td class="yes">○</td></tr>
</tbody></table></div>
<p class="note-s">{SEARCH} 広告用間取り図は寸法も縮尺もなく<b>見積には使えない</b>。この価格帯を作図代行の相場と混同しないこと。1000sqft（約93m²）で換算すると Canvas は約2.2〜2.9万円となり、日本の原図起こしと同水準になる。</p>''')

P.append('''<div class="banner">
<p class="t"><span class="dot"></span>本調査で最大の空白</p>
<p>日本の作図代行は豊富・安価・高速で、しかも DXF が標準の納品形式である。ところが調べた限り<b>すべて既存図面のトレースが前提</b>で、3Dスキャンや点群を入力として受け付ける事業者を発見できなかった。日本語での検索でも点群対応の作図代行は出てこない。</p>
<p>つまり「日本で iPhone LiDAR スキャンを送ると寸法入り現況図が DXF で返ってくる」サービスは、商品化された形では存在しない可能性が高い。ここが確認できれば、自社スキャン導入の必要性そのものが決まる。</p>
</div>''')

# ── population ────────────────────────────────────────────────────────
byt = collections.Counter(c.get('type') for c in C)
jp = sum(1 for c in C if re.search(r'[぀-ヿ一-鿿]', c.get('vendor','')))
lid = sum(1 for c in C if c.get('lidar')=='yes')
P.append(dim('06','母集団'))
P.append(head('117 製品を4つの出力形態に分類した',
 '単体アプリだけを見ると選択肢を落とす。業務システム内蔵の現調機能、点群止まりのツール、人が作図する代行サービスまでを同じ母集団に入れている。'))
P.append(f'''<div class="stats">
<div><span class="n">{len(C)}</span><span class="l">名寄せ後の製品数</span></div>
<div><span class="n">{jp}</span><span class="l">日本ベンダー</span></div>
<div><span class="n">{lid}</span><span class="l">LiDAR 対応と記載</span></div>
<div><span class="n">21</span><span class="l">立証を実施した製品</span></div>
</div>''')
rws=[]
for c in sorted(C, key=lambda x:(0 if re.search(r'[぀-ヿ一-鿿]',x.get('vendor','')) else 1, x['product'])):
    jpv = '日本' if re.search(r'[぀-ヿ一-鿿]', c.get('vendor','')) else '海外'
    li = {'yes':'<span class="yes">○</span>','no':'<span class="no">×</span>'}.get(c.get('lidar'),'<span class="na">—</span>')
    rws.append(f'<tr><td class="name">{e(c["product"])}<span class="vendor">{e(c.get("vendor"))}</span></td>'
               f'<td class="num">{jpv}</td><td class="num">{e(c.get("type"))}</td><td class="num">{li}</td>'
               f'<td>{e(c.get("note"))[:170]}</td></tr>')
P.append(f'''<div class="scroller"><table>
<thead><tr><th>型</th><th>中身</th><th class="num">件数</th></tr></thead><tbody>
<tr><td class="name">A</td><td>端末内で自動作図、その場で平面図</td><td class="num">{byt.get('A',0)}</td></tr>
<tr><td class="name">B</td><td>クラウド処理 → 図面が返る</td><td class="num">{byt.get('B',0)}</td></tr>
<tr><td class="name">C</td><td>点群・メッシュ止まり、作図はCADで人が行う</td><td class="num">{byt.get('C',0)}</td></tr>
<tr><td class="name">D</td><td>スキャン送付 → 人が作図して納品</td><td class="num">{byt.get('D',0)}</td></tr>
<tr><td class="name">未分類</td><td>出力形態を確認できていない</td><td class="num">{byt.get('unknown',0)}</td></tr>
</tbody></table></div>
<details class="more"><summary>母集団 {len(C)} 件をすべて表示</summary>
<div class="scroller" style="border:none;box-shadow:none;border-radius:0"><table>
<thead><tr><th>製品 / 提供元</th><th class="num">地域</th><th class="num">型</th><th class="num">LiDAR</th><th>発見時の記載（検索由来・未検証）</th></tr></thead>
<tbody>{''.join(rws)}</tbody></table></div></details>''')

# ── exclusions ────────────────────────────────────────────────────────
P.append(dim('07','除外と注意'))
P.append(head('候補から外すべきもの、条件付きのもの',
 '実在性と事業継続性の確認は、体裁の良いサイトだけで実体がない製品を弾くために行った。1件、実在を確認できないものがあった。'))
P.append(f'''<div class="scroller"><table>
<thead><tr><th>製品</th><th>判定</th><th>理由</th></tr></thead><tbody>
<tr><td class="name">i3Dfolio</td><td><span class="pill ng">除外推奨</span></td><td>6通りの検索で自社サイト以外に一切ヒットせず。App Store掲載なし、企業名・開発者名なし、レビューなし、バージョン・更新日なし。サイト自身が「version one」「solo developer」と記載。さらに「課金なし・機能制限なし」と「業務アカウントに権限管理・資材管理」を同一サイトで併記しており矛盾</td></tr>
<tr><td class="name">Re:BIM</td><td><span class="pill hold">条件付き</span></td><td>iPad Pro 専用で iPhone 対応の記載がない。価格が完全非公開。賃貸の退去修繕に業種特化</td></tr>
<tr><td class="name">room me</td><td><span class="pill hold">条件付き</span></td><td>原状回復工事に特化。DXF出力の記載なし</td></tr>
<tr><td class="name">だれでも現地調査</td><td><span class="pill hold">条件付き</span></td><td>コスト削減効果が同社の職人マッチング経由の発注を前提としており、自社施工では効果が変わる可能性</td></tr>
<tr><td class="name">CamPlan</td><td><span class="pill hold">要確認</span></td><td>App Store レビューに無料トライアル後の想定外課金とクラッシュへの言及。更新日・バージョンが未取得</td></tr>
<tr><td class="name">RoomPlot</td><td><span class="pill hold">要確認</span></td><td>個人開発者。第三者レビューなし、バージョン・更新日不明。面積は室面積のみ</td></tr>
<tr><td class="name">間取りスキャナー</td><td><span class="pill hold">評価不能</span></td><td>記述は用途①に最も近いが、料金が公開情報に一切なく比較できない。要問い合わせ</td></tr>
</tbody></table></div>
<p class="note-s">{SEARCH} 「記載なし」は「非対応」ではない。除外推奨としたのは i3Dfolio のみで、根拠は機能ではなく<b>実在と継続性が確認できないこと</b>にある。</p>''')

# ── studies ───────────────────────────────────────────────────────────
P.append(dim('08','精度の第三者検証'))
P.append(head('Apple LiDAR の精度を実測した文献',
 '採否の基準は一行、<b>測定条件と数値が書いてあるか</b>。レビュー記事は除外している。ただし本文が取得できていないため、以下は書誌情報と検索記録の段階にとどまる。'))
def _study_row(x):
    yr = ' / ' + str(x['year']) if x.get('year') else ''
    warn = ' <span class="chip unknown">要再確認</span>' if 'LOW_CONFIDENCE' in x.get('verified','') else ''
    return ('<tr><td class="name" style="white-space:normal;max-width:24em">' + e(x['title'])
            + '<span class="vendor">' + e(x.get('authors')) + yr + ' · ' + e(x.get('venue')) + '</span></td>'
            + '<td>' + e(x.get('reference_instrument')) + '</td>'
            + '<td>' + e(x.get('reported_error')) + warn + '</td>'
            + '<td>' + e(x.get('conditions')) + '</td></tr>')
trows=''.join(_study_row(x) for x in S)
P.append(f'''<div class="scroller"><table>
<thead><tr><th>文献</th><th>基準器</th><th>報告された誤差</th><th>測定条件</th></tr></thead>
<tbody>{trows}</tbody></table></div>
<p class="note-s">屋内・室スケールでトータルステーションや地上型レーザースキャナと直接比較したものが、この用途には最も近い。用途①の足切り（床面積±3%、主要寸法±50mm）に照らすと報告値は概ね桁として足りているが、確認は自前の実測で行う。</p>''')

# ── next ──────────────────────────────────────────────────────────────
P.append(dim('09','次の一手'))
P.append(head('この続きに必要なこと',
 '設計・スキーマ・採点規則・実測プロトコルは確定済みで、リポジトリに収録してある。止まっているのはデータ取得だけなので、接続さえ通れば同じ手順をそのまま再実行できる。'))
P.append('''<div class="wl">
<div><h3>1. ネットワークの解放</h3><p>ベンダードメイン・App Store・学術出版社への接続を許可した環境で再実行する。現状は GitHub 等のみのアローリストで、これが唯一の障害。</p></div>
<div><h3>2. 価格の確定</h3><p>Metaroom・ArcSite・magicplan・Polycam は公式 Pricing ページの実取得が必須。ディレクトリサイトの数字は互いに矛盾しており使えない。間取りスキャナーはキャドネットへ直接問い合わせ。</p></div>
<div><h3>3. 開口部控除の確認</h3><p>見積用途で最も効く一点。magicplan 以外は全製品で未確認。壁面積からドア・窓が自動で引かれるかを各社ヘルプで確認する。</p></div>
<div><h3>4. 日本の代行の点群受付</h3><p>iPhone LiDAR スキャンを受け付けて寸法入り現況図を返す日本の事業者が存在するかを電話で確認する。存在するなら自社導入が不要になる可能性がある。</p></div>
<div><h3>5. サンプルDXFの回収</h3><p>各社のサンプルDXFを実際に CAD で開く。壁の閉合、レイヤ分け、寸法の有無、日本語の文字化け、単位が mm か。ここで初めて図面精度が主張から事実になる。</p></div>
<div><h3>6. 同一物件テスト</h3><p>正解寸法を先に確定し、現場担当者本人が補助者・三脚なし、家具を動かさずに全候補を通す。2回スキャンして再現性を見る。機内モードで1回。ここで順位が確定する。</p></div>
</div>''')

open('report.html','w').write(open('_head.part').read() + '\n'.join(P) + open('_foot.part').read())
print('rendered', len(open('report.html').read()), 'bytes')
