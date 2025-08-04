# アプリ作成その 3

## 概要

`ビュー`とは、Django のアプリケーションにおいて特定の機能を提供するウェブペー ジの「型 (type)」であり、各々のテンプレートを持っています  
例えばブログアプリケーションなら、以下のようなビューがあるでしょう:

    ・Blog ホームページ - 最新エントリーをいくつか表示

    ・エントリー詳細ページ - 1 エントリーへのパーマリンク (permalink) ページ

    ・年ごとのアーカイブページ - 指定された年のエントリーの月を全て表示

    ・月ごとのアーカイブページ - 指定された月のエントリーの日をすべて表示

    ・日ごとのアーカイブページ - 指定された日の全てのエントリーを表示

    ・コメント投稿 - エントリーに対するコメントの投稿を受付

投票アプリケーションでは、以下 4 つのビューを作成します:

    ・質問 "インデックス" ページ -- 最新の質問をいくつか表示

    ・質問 "詳細" ページ -- 結果を表示せず、質問テキストと投票フォームを表示

    ・質問 "結果" ページ -- 特定の質問の結果を表示

    ・投票ページ -- 特定の質問の選択を投票として受付

Django では、ウェブページとコンテンツはビューによって提供されます  
各ビューは単純に Python 関数 (クラスベースビューの場合はメソッド) として実装されています  
Django はビューを、リクエストされた URL (正確には、URL のドメイン以降の部分) から決定します

URL パターンは、URL を単に一般化したものです。たとえば、 `/newsarchive/<year>/<month>/` などです

URL からビューを得るために、Django は「URLconf」と呼ばれているものを使います。URLconf は URL パターンをビューにマッピングします

## もっとビューを書いてみる

以下の view を polls/views.py に追加しましょう  
これから追加する view では引数を取ります

```
# polls/views.py

def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
```

次に、path()コーるを追加して、polls.urls モジュールと紐づけます

```
# polls/urls.py

from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/5/
    path("<int:question_id>/", views.detail, name="detail"),
    # ex: /polls/5/results/
    path("<int:question_id>/results/", views.results, name="results"),
    # ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
```

ブラウザで "/polls/34/" を見てください。 detail() 関数が実行され、URL で指定した ID が表示されます  
"/polls/34/results/" と "/polls/34/vote/" も試してみてください――これらはプレースホルダの結果と投票ページを表示します

誰かが Web サイトの 「/polls/34/」 をリクエストすると、 Django は ROOT_URLCONF に指定されている Python モジュール mysite.urls をロードします  
そのモジュール内の urlpatterns という変数を探し、順番にパターンを検査していきます  
polls/ にマッチした箇所を見つけた後、一致した文字列 ("polls/") を取り除き、残りの文字列である "34/" を次の処理のために 『polls.urls』 の URLconf に渡します  
これは '<int：question_id>/' に一致し、結果として下記のように detail() が呼び出されます

`detail(request=<HttpRequest object>, question_id=34)`

question_id=34 の部分は '<int:question_id>' から来ています  
山括弧を使用すると、URL の一部が「キャプチャ」され、キーワード引数としてビュー関数に送信します  
 文字列の :question_id 部分は、一致するパターンを識別するために使用される名前を定義し、int 部分は、URL パスのこの部分に一致するパターンを決定するコンバータです  
 コロン (:) はコンバータとパターン名を区切ります

## 実際に動作するビューを書く

各ビューには二つの役割があります:  
一つはリクエストされたページのコンテンツを含む HttpResponse オブジェクトを返すこと、
もう一つは Http404 のような例外の送出です  
それ以外の処理はユーザ次第です

ビューはデータベースからレコードを読み出しても、読み出さなくてもかまいません  
Django のテンプレートシステム、あるいはサードパーティの Python テンプ レートシステムを使ってもよいですし、使わなくてもかまいません  
PDF ファイルを生成しても、 XML を出力しても、 ZIP ファイルをその場で生成してもかまいません  
Python ライブラリを使ってやりたいことを何でも実現できます

Django にとって必要なのは HttpResponse か、あるいは例外です。

チュートリアルその 2 で解説した Django のデータベース API を使ってみましょう  
試しに次のような index() ビューを作ります  
これは、システム上にある最新の 5 件の質問項目をカンマで区切り、日付順に表示するビューです:

```
# polls/views.py

from django.http import HttpResponse
from .models import Question

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    output = ", ".join([q.question_text for q in latest_question_list])
    return HttpResponse(output)

# Leave the rest of the views (detail, results, vote) unchanged
```

このコードには問題があります  
ビューの中で、ページのデザインがハードコードされています  
ページの見栄えを変更するたびに、Python コードを編集する必要があります  
Django のテンプレートシステムを使って、ビューから使用できるテンプレートを作成し、Python からデザインを分離しましょう

最初に、 polls ディレクトリの中に、 templates ディレクトリを作成します  
Django はそこからテンプレートを探します

プロジェクトの TEMPLATES には、Django がどのようにテンプレートをロードしレンダリングするかが書かれています  
デフォルトの設定ファイルでは、 DjangoTemplates バックエンドが設定されており、その APP_DIRS のオプションが True になっています  
規約により、 DjangoTemplates は INSTALLED_APPS のそれぞれの "templates" サブディレクトリを検索します

先ほど作成した templates ディレクトリ内で polls というディレクトリを作成し、さらにその中に index.html というファイルを作成してください  
つまり、テンプレートは polls/templates/polls/index.html に書く必要があります  
app_directories テンプレートローダは前述のように動くため、Django 内でこのテンプレートを単に polls/index.html のように参照できます

```
# テンプレートの名前空間

作ったテンプレートを (polls という別のサブディレクトリを作らずに) 直接 polls/templates の中に置いてもいいのではないか、と思うかもしれませんね
しかし、それは実際には悪い考えです
Django は、名前がマッチした最初のテンプレートを使用するので、もし 異なる アプリケーションの中に同じ名前のテンプレートがあった場合、Django はそれらを区別することができません
そのため、Django に正しいテンプレートを教えてあげる必要がありますが、一番簡単な方法は、それらに 名前空間を与える ことです
アプリケーションと同じ名前をつけた もう一つの ディレクトリの中にテンプレートを置いたのは、そういうわけなのです
```

テンプレートには次のコードを書きます:

```
# polls/templates/polls/index.html

{% if latest_question_list %}
    <ul>
    {% for question in latest_question_list %}
        <li><a href="/polls/{{ question.id }}/">{{ question.question_text }}</a></li>
    {% endfor %}
    </ul>
{% else %}
    <p>No polls are available.</p>
{% endif %}
```

```
# 注釈

# ートリアルを短くするために、すべてのテンプレートの例では不完全なHTMLを使用しています。独自のプロジェクトでは 完全な HTML ドキュメント を使用する必要があります。
```

このテンプレートを使用するために polls/views.py の index ビューを更新してみましょう:

```
# polls/viwes.py

from django.http import HttpResponse
from django.template import loader
from .models import Question

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    template = loader.get_template("polls/index.html")
    context = {"latest_question_list": latest_question_list}
    return HttpResponse(template.render(context, request))
```

このコードは、 polls/index.html というテンプレートをロードし、そこにコンテキストを渡します  
コンテキストは、テンプレート変数名を Python オブジェクトにマッピングする辞書です

ブラウザで "/polls/" を開くと、箇条書きのリストが表示されるはずです（リストには、 チュートリアルその 2 で作った "What's up" という質問が入っていますね）  
リンクは質問の詳細ページを指します

## ショートカット

テンプレートをロードしてコンテキストに値を入れ、テンプレートをレンダリングした結果を HttpResponse オブジェクトで返す、というイディオムは非常によく使われます  
Django はこのためのショートカットを提供します  
これを使って index() ビューを書き換えてみましょう:

```
# polls/views.py

from django.shortcuts import render
from .models import Question

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)
```

全部の view をこのように書き換えてしまえば、 loader や HttpResponse を import する必要はなくなります (detail 、 results 、 vote を引き続きスタブメソッドにするなら、 HttpResponse はそのままにしておいたほうがいいでしょう)

render() 関数は、第 1 引数として request オブジェクトを、第 2 引数としてテンプレート名を、第 3 引数（任意）として辞書を受け取ります  
この関数はテンプレートを指定のコンテキストでレンダリングし、その HttpResponse オブジェクトを返します

## 404 エラーの送出

さて、質問詳細ビューに取り組みましょう  
このページは、指定された投票の質問文を表示するものです。ビューは次のようになります:

```
# polls/views.py

from django.http import Http404
from django.shortcuts import render

from .models import Question


# ...
def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/detail.html", {"question": question})
```

新しい概念が出てきました。このビューは、リクエストした ID を持つ質問が存在しないときに Http404 を送出します

polls/detail.html テンプレートに何を書けばよいかは後で解説しますが、さしあたって上の例題を動かしたければ、単に:

```
# polls/templates/polls/detail.html

{{ question }}
```

と書いておいてください

## ショートカット: get_object_or_404()

get() を実行し、オブジェクトが存在しない場合には Http404 を送出することは非常によく使われるイディオムです  
Django はこのためのショートカットを提供しています  
ショートカットを使って、 detail() ビューを書き換えてみましょう:

```
# polls/views.py

from django.shortcuts import get_object_or_404, render

from .models import Question


# ...
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})
```

get_object_or_404() 関数は、Django モデルを第一引数に、任意の数のキーワード引数を取り、モデルのマネージャの get() 関数に渡します  
オブジェクトが存在しない場合は Http404 を発生させます

```
# 設計思想

なぜ ObjectDoesNotExist 例外を高水準で自動的にキャッチせず、ヘルパー関数 get_object_or_404() を使うのでしょうか
また、なぜモデル API に ObjectDoesNotExist ではなく、 Http404 を送出させるのでしょうか?

なぜなら、それはモデル層とビュー層とを密結合させることになるからです
Django の最も重要な設計目標の一つは、疎結合を維持することです
django.shortcuts には結合がコントロールされたいくつかのモジュールが用意されています
```

get_list_or_404() という関数もあります  
この関数は get_object_or_404() と同じように動きますが、 get() ではなく、 filter() を使います  
リストが空の場合は Http404 を送出します

## テンプレートシステムを使う

投票アプリの detail() ビューに戻りましょう  
コンテキスト変数を question とすると、 polls/detail.html テンプレートは次のようになります:

```
# polls/templates/polls/detail.html

<h1>{{ question.question_text }}</h1>
<ul>
{% for choice in question.choice_set.all %}
    <li>{{ choice.choice_text }}</li>
{% endfor %}
</ul>
```

テンプレートシステムは、変数の属性にアクセスするためにドット検索の構文を使用します  
{{ question.question_text }} を例にすると、はじめに Django は question オブジェクトに辞書検索を行います  
それに失敗したら、今度は属性として検索を行い、このケースの場合は成功します  
もし属性の検索に失敗すると、リストインデックスでの検索を行います

メソッドの呼び出しは {% for %} ループの中で行われています  
question.choice_set.all は、 Python コードの question.choice_set.all() と解釈されます  
その結果、Choice オブジェクトからなるイテレーション可能オブジェクトを返し、 {% for %} タグで使えるようになります

テンプレートの詳しい動作は テンプレートガイド を参照してください

## テンプレート内のハードコードされた URL を削除

polls/index.html テンプレートで質問へのリンクを書いたとき、リンクの一部は次のようにハードコードされていました:

```
<li><a href="/polls/{{ question.id }}/">{{ question.question_text }}</a></li>
```

このハードコードされた密結合のアプローチの問題は、プロジェクトにテンプレートがたくさんある場合、URL の変更が困難になってしまうことです  
しかし、 polls.urls モジュール の path() 関数で name 引数を定義したので、テンプレートタグの {％ url ％} を使うことで URL 設定で定義されている特定の URL パスへの依存をなくすことができます:

```
<li><a href="{% url 'detail' question.id %}">{{ question.question_text }}</a></li>
```

これが機能するのは、 polls.urls モジュールに指定された URL の定義を検索するからです  
'detail' の URL 名は以下の箇所で定義されています:

```
...
# the 'name' value as called by the {% url %} template tag
path("<int:question_id>/", views.detail, name="detail"),
...
```

## URL 名の名前空間

このチュートリアルプロジェクトが持つアプリは polls アプリ 1 つだけです  
実際の Django プロジェクトでは、5 個、10 個、20 個、あるいはそれ以上のアプリがあるかもしれません  
Django はどうやってこれらの間の URL 名を区別するのでしょうか？  
例えば、 polls アプリは detail ビューを含みますが、同じプロジェクトにブログのためのアプリがあり、そのアプリも同名のビューを含むかもしれません  
{% url %} テンプレートタグを使ったとき、 Django はどのアプリのビューに対して url を作成すればいいでしょうか？ これを Django にどう知らせればいいでしょうか

答えは、URLconf に名前空間を追加することです  
polls/urls.py ファイル内で、アプリケーションの名前空間を設定するために app_name を追加します:

```
# polls/urls.py

from django.urls import path
from . import views

app_name = "polls"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
```

次に polls/index.html テンプレートを変更します。以下の形から、

```
# polls/templates/polls/index.html

<li><a href="{% url 'detail' question.id %}">{{ question.question_text }}</a></li>
```

以下の形にし、名前空間付きの詳細ビューを指すようにします:

```
# polls/templates/polls/index.html

<li><a href="{% url 'polls:detail' question.id %}">{{ question.question_text }}</a></li>
```

ビューを書けるようになったら、 チュートリアルその 4 に進んで、簡単なフォームの処理と汎用ビューについて学びましょう
