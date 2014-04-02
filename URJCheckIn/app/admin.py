from django.contrib import admin
from models import Degree, Subject, Room, UserProfile, Lesson, CheckIn, ForumComment, Timetable, LessonComment, Building

admin.site.register(Degree)
admin.site.register(Subject)
admin.site.register(Room)
admin.site.register(UserProfile)
admin.site.register(Lesson)
admin.site.register(CheckIn)
admin.site.register(ForumComment)#TODO no deberian poder poner nuevos o modificarlos, solo borrarlos
admin.site.register(Timetable)
admin.site.register(LessonComment)
admin.site.register(Building)
