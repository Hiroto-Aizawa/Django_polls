# アプリ作成その 2

## Database の設定

mysite/settings.py を開いて、データベースの設定を確認すると、デフォルトでは SQLite を使用するようになっています  
別のデータベースを使用したい場合は、[データベースを動かす](https://docs.djangoproject.com/ja/5.2/topics/install/#database-installation)を参考にしてください

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

同じファイル内にある「INSTALLED_APPS」に注意してください  
これは Django のインスタンスの中で有効化されているすべての Django アプリケーションの名前を保持しています  
デフォルトでは、「INSTALLED_APPS」には以下のアプリケーションが入っています

```
django.contrib.admin - 管理（admin）サイト。まもなく使います

django.contrib.auth - 認証システム

django.contrib.contenttypes - コンテンツタイプフレームワーク

django.contrib.sessions - セッションフレームワーク

django.contrib.messages - メッセージフレームワーク

django.contrib.staticfiles - 静的ファイルの管理フレームワーク
```

これらの機能は良く使われるのでデフォルトで付属しています

これらのアプリケーションは最低 1 つデータベースのテーブルを使うので、使い始める前にデータベースにテーブルを作る必要があります

以下のコマンドを実行してデータベースの作成をします

`$ python3 manage.py migrate`

migrate コマンドは「INSTALLED_APPS」の設定を参照するとともに、mysite/settings.のデータベース設定に従って必要なすべてのデータベースのテーブルを作成します  
このデータベースマイグレーションはアプリと共に配布されます

マイグレーションを実施するたび、メッセージを見ることになります  
もしこれに興味が引かれたら、Django が作成したテーブルを表示するために、コマンドラインクライアントであなたのデータベースの種類に合わせて、  
**dt**\(PostgreSQL)、**SHOW TABLES**;(MySQL)、**.tables**(SQlite)、 もしくは **SELECT TABLE_NAME FROM USER_TABLES;**(Oracle)とタイプしてみましょう

## モデルの作成

これからモデルを定義します。モデルは本質的には、データベースのレイアウトと、それに付随するメタデータです。

```
# 設計思想

モデルは、手持ちのデータに対する唯一無二の決定的なソースです
モデルには自分が格納したいデータにとって必要不可欠なフィールドと、そのデータの挙動を納めます
Djangoは※DRY則(https://docs.djangoproject.com/ja/5.2/misc/design-philosophies/#dry)に従っています
Djangoのモデルの目的は、ただ一つの場所でデータモデルを定義し、そこから自動的にデータを取り出すことにあります

これはマイグレーションを含みます
```

これから開発する簡単な poll アプリケーションでは、Question と Choice の 2 つのモデルを作成します  
Poll には question と publication date の情報があります

Choice には選択肢のテキストと vote という 2 つのフィールドがあります
各 Choice には 1 つの Question が関連付けられています

Django では、こうした概念を簡単な Python クラスで表現できます  
polls/models.py を以下のように編集します

```
# polls/models.py
from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
```

各モデルは一つのクラスで表現され、いずれも **django.db.models.Model** のサブクラスです  
各モデルには風九数のクラス変数があり、個々のクラス変数はモデルのデータベースフィールドを表現しています

Choice の question では`models.ForeignKey()`を使用して、Question とのリレーションが定義されています  
これは、それぞれの Choice が一つの Question と関連付けられることを Django に伝えます  
Django は多対一、多対多、そして一対一のようなデータベースリレーションシップをすべてサポートします

## モデルを有効にする

Django はほんのわずかなコードをモデルに書くだけで、たくさんの情報を知ることができます  
このコードを使って Django は：  
・アプリケーションのデータベーススキーマを作成(CREATE TABLE 文を実行)できます

・Question や Choice オブジェクトに Python からアクセスするためのデータベース API を作成できます

でものその前に、polls アプリケーションをインストールしたことをプロジェクトに教える必要があります

```
# 設計思想

Djangoアプリケーションは「プラガブル(pluggable)」です
アプリケーションは特定のDjangoインストールに結びついていないので、
アプリケーションを複数のプロジェクトで使ったり、単体で配布したりできます
```

アプリケーションをプロジェクトに含めるには、構成クラスへの参照を「INSTALLED_APPS」設定に追加する必要があります  
PollsConfig クラスは、polls/apps.py にあるので、ドットつなぎのパスは'polls.apps.PollsConfig'となります

mysite/settings.py を編集し、「INSTALLED_APPS」設定にドットつなぎのパスを追加します  
すると下記のようになります

```
# mysite/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'polls.apps.PollsConfig',
]
```

これで Django は、polls アプリケーションが含まれていることを認識できます

もう一つコマンドを実行しましょう

`$ python3 manage.py makemigrations polls`

実行後に以下の内容が表示されるはずです

```
Migrations for 'polls':
  polls/migrations/0001_initial.py
    + Create model Question
    + Create model Choice
```

`makemigrations`を実行することで、Django モデルに変更があったこと(この場合、新しいものを作成しました)を伝え、そして変更をマイグレーションの形で保存することができました

マイグレーションは Django がモデル(そしてデータベーススキーマ)の変更を保存する方法です  
マイグレーションは、ディスク上のただのファイルです  
望むならば、新しいモデルのためのマイグレーションファイルを`polls/migratons/0001_initial.py`を読むこともできます

Django には、マイグレーションをあなたの代わりに実行し、自動でデータベーススキーマを管理するためのコマンドがあります。  
これは`migrate`と呼ばれるコマンドで、初回に一度実行しています  
しかし最初は、マイグレーションがどんな SQL を実行するのか見てみましょう  
`sqlmigrate`コマンドはマイグレーションの名前を引数にとって SQL を返します

`$ python3 manage.py sqlmigrate polls 0001`

次のような結果が表示されるはずです(読みやすくするために再フォーマットしました)

```
BEGIN;
--
-- Create model Question
--
CREATE TABLE "polls_question" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "question_text" varchar(200) NOT NULL,
    "pub_date" datetime NOT NULL
);
--
-- Create model Choice
--
CREATE TABLE "polls_choice" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "choice_text" varchar(200) NOT NULL,
    "votes" integer NOT NULL,
    "question_id" bigint NOT NULL REFERENCES
    "polls_question" ("id")
    DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX "polls_choice_question_id_c5b4b260" ON "polls_choice" ("question_id");

COMMIT;
```

以下に注意してください：

**sqlmigrate**コマンドは実際にはデータベースにマイグレーションを実行しませんでした。  
ただ、Django が必要としている SQL が何であるかをスクリーンに表示するだけです  
これは Django が何をしようとしているかを確認したり、データベース管理者に変更のための SQL スクリプトを要求されているときに役立ちます

興味があれば`python3 manage.py check`を実行することもできます  
これはマイグレーションを作成したり、データベースにふれることなく、プロジェクトに何か問題がないかを確認します

migrate コマンドを再度実行し、モデルのテーブルをデータベースに作成します

`$ python3 manage.py migrate`

以下のような出力がでれば成功です

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, polls, sessions
Running migrations:
  Applying polls.0001_initial... OK
```

migrate コマンドはすべての適用されていないマイグレーション(Django はデータベース内の django_migrations と呼ばれる特別なテーブルを利用してどれが適用されているかを追跡しています)を捕捉してデータベースに対してそれを実行します

モデルの変更を実施するための 3 ステップガイドを覚えておいてください：

```
・モデルを変更する(models.pyの中のもの)

・これらの変更のためのマイグレーションを作成するために`$ python3 manage.py makemigrations`を実行する

・データベースにこれらの変更を適用するために`$ python3 manage.py migrate`を実行する
```

マイグレーションの作成と適用のコマンドが分割されている理由は、マイグレーションをバージョン管理システムにコミットし、アプリとともに配布するためです  
これによって、開発が容易になるだけでなく、他の開発者や本番環境にとって使いやすいものになります

## API で遊んでみる

## Django Admin の紹介

まず初めに admin サイトにログインできるユーザーを作成する必要があります  
以下のコマンドを実行してスーパーユーザーを作成します

`python3 manage.py createsuperuser`

ユーザー作成の際に以下の入力が求められるので自由に設定してください

・ユーザー名  
・メールアドレス  
・パスワード

最後のパスワードの入力が終わり、作成が完了すると以下のようになっているはずです

```
Password: **********
Password (again): *********
Superuser created successfully.
```

## 開発サーバーの起動

Django admin サイトはデフォルトで有効化されます  
サーバーを起動して admin サイトにアクセスしましょう

`python3 manage.py runserver`

サーバーが起動したら、「http://127.0.0.1:8000/admin/login/?next=/admin/」にアクセスします

先ほど入力したユーザー名とパスワードを入力して、ログインしましょう

### Poll アプリを admin 上で編集できるようにする

Question オブジェクトが admin インターフェースを持つということを、admin に伝える必要があります  
そのために、polls/admin.py を以下のように編集しましょう

```
# polls/admin.py
from django.contrib import admin

from .models import Question

admin.site.register(Question)
```

これで admin 上で Poll アプリの編集ができるようになりました
