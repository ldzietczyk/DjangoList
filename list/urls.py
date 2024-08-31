from django.urls            import path
from .                      import views
from django.views.generic   import TemplateView


urlpatterns = [
    path('', views.indexv, name='index'),
    path('form/', views.formv, name='form'),
    path('login/', views.loginv.as_view(), name='login'),
    path('logout/', views.logoutv.as_view(), name='logout'),
    path('<path:path>', TemplateView.as_view(template_name="main/404.html"), name="404"),
]