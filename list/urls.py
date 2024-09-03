from django.urls            import path
from .                      import views
from django.views.generic   import TemplateView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.indexv, name='index'),
    path('form/', views.formv, name='form'),
    path('confirm-update/', views.confirm_update, name='confirm_update'),
    path('login/', views.loginv.as_view(), name='login'),
    path('logout/', views.logoutv.as_view(), name='logout'),
    path('success/', views.successv, name='success'),
    path('report/', views.reportv, name='report'),
    path('<path:path>', TemplateView.as_view(template_name="main/404.html"), name="404"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)