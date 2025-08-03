from django.urls import path
from . import views

urlpatterns = [
    # 同じ階層のview.pyで定義されているindex関数を呼び出す
    # nameはURLの名前を指定するためのもので、後でURLを参照する際に使用する
    path("", views.index, name="index"),
]