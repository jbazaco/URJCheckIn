from django.contrib import admin
from models import Degree, Subject, Room, UserProfile, ClassReview, Lesson, CheckIn, ForumComment, TimeTable

admin.site.register(Degree)
admin.site.register(Subject)
admin.site.register(Room)
admin.site.register(UserProfile)
admin.site.register(ClassReview)#no deberian poder cambiarlo los administradores
admin.site.register(Lesson)
admin.site.register(CheckIn)
admin.site.register(ForumComment)#no deberian poder poner nuevos o modificarlos, solo borrarlos
admin.site.register(TimeTable)
