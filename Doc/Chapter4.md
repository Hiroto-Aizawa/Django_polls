# アプリ作成その 4

## 簡単なフォームを書く

前回のチュートリアルで作成した投票詳細テンプレート ("polls/detail.html") を更新して、HTML の <form> 要素を入れましょう

```
# polls/templates/polls/detail.html

<form action="{% url 'polls:vote' question.id %}" method="post">
{% csrf_token %}
<fieldset>
    <legend><h1>{{ question.question_text }}</h1></legend>
    {% if error_message %}<p><strong>{{ error_message }}</strong></p>{% endif %}
    {% for choice in question.choice_set.all %}
        <input type="radio" name="choice" id="choice{{ forloop.counter }}" value="{{ choice.id }}">
        <label for="choice{{ forloop.counter }}">{{ choice.choice_text }}</label><br>
    {% endfor %}
</fieldset>
<input type="submit" value="Vote">
</form>
```

簡単に説明:

    ・上のテンプレートは、各質問の選択肢のラジオボタンを表示するものです
    各ラジオボタンの value は、関連する質問の選択肢の ID です。各ラジオボタンの name は "choice" です
    つまり、投票者がラジオボタンの 1 つを選択し、フォームを送信すると、POST データ choice=# （#は選んだ選択肢の ID）が送信されます。これは、HTML フォームの基本的な概念です

    ・フォームの action を {% url 'polls:vote' question.id %} に設定し、method="post" を指定しています
    (method="get" ではなく) method="post" を使用することは非常に重要です。なぜなら、フォームの送信はサーバ側のデータの更新につながるからです
    サーバ側のデータを更新するフォームを作成する場合は、method="post" を使いましょう
    これは、 Django 固有のものではなく、いわばウェブ開発の王道です

    ・forloop.counter は、 for タグのループが何度実行されたかを表す値です

    ・(データを改ざんされる恐れのある) POST フォームを作成しているので、クロスサイトリクエストフォージェリを気にする必要があります
    ありがたいことに、 Django にはそれに対処するための便利な仕組みがあるので、あまり心配する必要はありません
    簡単に言うと、自サイト内の URL を対象とする POST フォームにはすべて、 {% csrf_token %} テンプレートタグを使うべきです

送信されたデータを処理するための Django のビューを作成しましょう  
チュートリアルその 3 で、以下のような投票アプリケーションの URLconf を作成したことを思い出しましょう:

```
# polls/urls.py

path("<int:question_id>/vote/", views.vote, name="vote"),
```

このとき、vote()関数のダミー実装も作成しました  
今度は本物を実装しましょう  
以下を polls/views.py に追加してください:

```
# polls/views.py

from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Choice, Question


# ...
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
```

このコードには、これまでのチュートリアルで扱っていなかったことがいくつか入っています:

    ・request.POST は辞書のようなオブジェクトです。キーを指定すると、送信したデータにアクセスできます
    この場合、 request.POST['choice'] は、選択された選択肢の ID を文字列として返します
    request.POST の値は常に文字列です。

    Django では、同じ方法で GET データにアクセスするために request.GET も提供しています。ただし、このコードでは、POST 呼び出し以外でデータが更新されないようにするために、request.POST を明示的に使っています。

    ・POST データに choice がなければ、 request.POST['choice'] は KeyError を送出します
    上のコードでは KeyError をチェックし、 choice がない場合にはエラーメッセージ付きの質問フォームを再表示します

    ・F("votes") + 1 は、 データベースに投票数を 1 増やすよう指示します

    ・choice のカウントをインクリメントした後、このコードは、 通常の HttpResponse ではなく HttpResponseRedirect を返します
    HttpResponseRedirect はひとつの引数（リダイレクト先のURL）をとります (この場合にURLをどう構築するかについては、以下のポイントを参照してください)

    上記の Python コメントが指摘するように、POST データが成功した後は常に HttpResponseRedirect を返す必要があります
    これは Django 固有のものではなく、Web開発における良いプラクティスです

    ・この例では、 HttpResponseRedirect コンストラクタの中で reverse() 関数を使用しています
    この関数を使うと、ビュー関数中での URL のハードコードを防げます
    関数には、制御を渡したいビューの名前と、そのビューに与える URL パターンの位置引数を与えます
    この例では、 チュートリアルその 3 で設定した URLconf を使っているので、 reverse() を呼ぶと、次のような文字列が返ってきます

    `"/polls/3/results/"`

    この 3 は question.id の値です
    リダイレクト先の URL は 'results' ビューを呼び出し、最終的なページを表示します

チュートリアルその 3 で触れたように、 request は HttpRequest オブジェクトです  
HttpRequest オブジェクトの詳細は リクエスト・レスポンスオブジェクトのドキュメント を参照してください

誰かが質問に投票すると、 vote() ビューは質問の結果ページにリダイレクトします。このビューを書いてみましょう

```
# polls/views.py

from django.shortcuts import get_object_or_404, render


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})
```

チュートリアルその 3 の detail() とほぼ同じです  
テンプレートの名前のみ違います。この冗長さは後で修正することにします

次に polls/results.html テンプレートを作成します:

```
# polls/templates/posll/results.html

<h1>{{ question.question_text }}</h1>

<ul>
{% for choice in question.choice_set.all %}
    <li>{{ choice.choice_text }} -- {{ choice.votes }} vote{{ choice.votes|pluralize }}</li>
{% endfor %}
</ul>

<a href="{% url 'polls:detail' question.id %}">Vote again?</a>
```

ブラウザで /polls/1/ を表示して投票してみましょう  
票を入れるたびに、結果のページが更新されていることがわかるはずです  
選択肢を選ばずにフォームを送信すると、エラーメッセージを表示されるはずです

## 汎用ビューを使う: コードが少ないのはいいことだ

detail() ( チュートリアルその 3 ) と results() ビューはとても簡単で、先程も述べたように冗長です  
投票の一覧を表示する index() ビューも同様です

これらのビューは基本的な Web 開発の一般的なケースを表します  
わち、 URL を介して渡されたパラメータに従ってデータベースからデータを取り出し、テンプレートをロードして、レンダリングしたテンプレートを返します  
これはきわめてよくあることなので、 Django では、汎用ビュー（generic view）というショートカットを提供しています

汎用ビューは一般的なパターンを抽象化し、Python コードを書かなくてもアプリを実装できるようになっています  
例えば、 ListView と DetailView は、それぞれ「オブジェクトの一覧を表示する」「特定のオブジェクトの詳細ページを表示する」という概念を抽象化したものです

これまで作成してきた poll アプリを汎用ビューシステムに変換して、 コードをばっさり捨てられるようにしましょう。変換にはほんの数ステップしかか かりません

そのステップは:

    1. URLconf を変換する。

    1. 古い不要なビューを削除する。

    1. 新しいビューに Django の汎用ビューを設定する。

詳しく見ていきましょう

```
# なぜコードを入れ替えるの？

一般に Django アプリケーションを書く場合は、まず自分の問題を解決するために汎用ビューが適しているか考えた上で、最初から汎用ビューを使い、途中まで書き上げたコードをリファクタすることはありません
ただ、このチュートリアルでは中核となるコンセプトに焦点を合わせるために、わざと「大変な」ビューの作成に集中してもらったのです

電卓を使う前に、算数の基本を知っておかねばならないのと同じです
```

## URLconf の修正

まず、 URLconf の polls/urls.py を開き、次のように変更します:

```
# polls/urls.py

from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
```

2 番目と 3 番目のパターンのパス文字列にマッチしたパターンの名前が、 <question_id> から <pk> に変わっていることに注意してください  
こうする必要があるのは、この後 DetailView という汎用ビューを使って detail() と results() ビューを置き換えますが、このビューでは URL から取得したプライマリーキーの値を "pk" として扱うためです

## views の修正

次に、古い index 、 detail 、と results のビューを削除し、代わりに Django の汎用ビューを使用します  
これを行うには、 polls/views.py ファイルを開き、次のように変更します:

```
# polls/views.py

from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    # same as above, no changes needed.
    ...
```

それぞれの汎用ビューには、どのモデルに対して動作するかを認識させる必要があります  
これは(DetailView と ResultsView の model = Question のように) model 属性を指定するか、( IndexView のように) get_queryset() 関数を定義することで実現できます

デフォルトでは、 DetailView 汎用ビューは <app name>/<model name>\_detail.html という名前のテンプレートを使います  
この場合、テンプレートの名前は "polls/question_detail.html" です。 template_name 属性を指定すると、自動生成されたデフォルトのテンプレート名ではなく、指定したテンプレート名を使うように Django に伝えることができます  
また、 results リストビューにも template_name を指定します  
これによって、 結果ビューと詳細ビューをレンダリングしたとき、（裏側ではどちらも DetailView ですが）それぞれ違った見た目になります

同様に、 ListView 汎用ビューは <app name>/<model name>\_list.html というデフォルトのテンプレートを使うので、 template_name を使って ListView に既存の "polls/index.html" テンプレートを使用するように伝えます

このチュートリアルの前の部分では、 question や latest_question_list といったコンテキスト変数が含まれるコンテキストをテンプレートに渡していました  
DetailView には question という変数が自動的に渡されます  
なぜなら、 Django モデル (Question) を使用していて、 Django はコンテキスト変数にふさわしい名前を決めることができるからです  
一方で、 ListView では、自動的に生成されるコンテキスト変数は question_list になります。これを上書きするには、 context_object_name 属性を与え、 latest_question_list を代わりに使用すると指定します  
この代替アプローチとして、テンプレートのほうを変えて、新しいデフォルトのコンテキスト変数の名前と一致させることもできます  
しかし、使用したい変数名を Django に伝えるだけのほうが簡単でしょう

サーバを実行して、新しく汎用ビューベースにした投票アプリケーションを使ってみましょう

汎用ビューの詳細は、汎用ビューのドキュメント を参照してください

フォームや汎用ビューを使いこなせるようになったら、 チュートリアルその 5 に進んで、投票アプリのテストについて学びましょう
