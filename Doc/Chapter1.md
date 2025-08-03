# アプリ作成その 1

## プロジェクトの作成

```
mysite/
    ♯まだ何もない
```

上記のようなルートディレクトにいる状態で下記コマンドを実行し、プロジェクト作成する  
これによって、ルートディレクトリ直下に、「mysite」ディレクトリが作成される

`$ django-admin startproject mysite`

startproject で何が作成されたかを確認する

```
mysite/                     # プロジェクトのコンテナ
    mysite/                 # Pythonパッケージ（importの際に使用する名前）
        __init__.py
        asgi.py             # プロジェクトをサーブするためのWSGI互換Webサーバーとのエントリーポイント
        setting.py          # Djangoプロジェクトの設定ファイル
        urls.py             # DjangoプロジェクトのURL宣言
        wsgi.py             # プロジェクトをサーブするためのWSGI互換Webサーバーとのエントリーポイント

    manage.py               # Djangoプロジェクトに対するコマンドの実行窓口
```

## 開発用サーバー

ルートディレクト（manage.py がある階層）に移動して、下記コマンドを実行する

`$ python3 manage.py runserver`

コマンドライン上で、以下のような出力が確認できれば、サーバーの起動に成功しています

```
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
August 03, 2025 - 15:17:07
Django version 5.2.4, using settings 'mysite.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

ブラウザで「http://127.0.0.1:8000/」にアクセスしてページが表示されるか確認しましょう

# Poll アプリケーションを作る

Django 内に追加する各アプリケーションは、所定の規則に従った Python パッケージで構成されます  
Django には基本的なディレクトリ構造を自動生成するユーティリティーが含まれているので、ディレクトリを作ることではなくコードを書くことに集中できます

```
【プロジェクトとアプリケーションの違い】

プロジェクト：
特定のウェブサイトの構成とアプリのコレクション
プロジェクト内には複数のアプリを含めることができ、アプリは複数のプロジェクトに存在できる。

アプリ：
ブログシステム、公的記録のデータベースなどの Web アプリケーション
```

アプリケーションを作成するには、**manage.py**と同じディレクトリに移動し、下記コマンドを実行します

`$ python3 manage.py startapp polls`

```
polls/
    migrations/
        __init__.py

    __init__.py
    admin.py
    apps.py
    models.py
    tests.py
    views.py
```

このディレクトリ構造が、polls アプリケーションの全体像です

## はじめてのビュー作成

polls/views.py を開いて、下記のコードを書きます

```
# polls/views.py

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
```

これをブラウザからアクセスするためには、URL にマッピングする必要があります  
そのためには、URL 設定「URLconf」を定義する必要があります  
この URL 設定は各 Django アプリ内で定義されており、urls.py という名前の Python ファイルです

polls アプリの URLconf を定義するには、以下の内容で polls/urls.py というファイルを作成します

```
# polls/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
]
```

現在の polls ディレクトリは以下のようになっているはずです

```
polls/
    migrations/
        __init__.py

    __init__.py
    admin.py
    apps.py
    models.py
    tests.py
    urls.py
    views.py
```

次のステップは、mysite プロジェクトのルートの URLconf に、polls.urls で定義された URLconf を含めることです  
そのためには、mysite/urls.py で django.urls.include をインポートし、urlpatterns リストに include()を追加します

```
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
]
```

path()関数には少なくとも 2 つの引数、route と view が必要です  
include()関数は、他の URLconf を参照するために使います  
Django が include()を見つけると、これまでに一致した URL の部分を切り捨てて、残りの文字をインクルードされた URLconf に渡して、さらに処理を続けます

```
【include()を使うとき】

他のURLパターンを含める際には、常にinclude()を使用するべきです
ただし、例外としてadmin.site.urlsがあります
これは、Djangoが提供するデフォルトの管理サイト用に事前に作成されたURLconfです
```

サーバーを起動して、「http://127.0.0.1:8000/polls/」にアクセスしましょう

polls/views.py で入力して「Hello, world. You're at the polls index.」が表示されれば OK です
