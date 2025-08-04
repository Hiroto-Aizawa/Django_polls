from django.urls import path
from . import views

app_name = "polls"  # アプリケーションの名前空間を指定
urlpatterns = [
    # 同じ階層のview.pyで定義されているindex関数を呼び出す
    # nameはURLの名前を指定するためのもので、後でURLを参照する際に使用する
    
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/5/
    path("specifics/<int:question_id>/", views.detail, name="detail"),
    # ex: /polls/5/results/
    path("<int:question_id>/results/", views.results, name="results"),
    # ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
]