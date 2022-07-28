from django.contrib import admin

from .models import Title, Review, Category, Genre, Comment


admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Comment)
