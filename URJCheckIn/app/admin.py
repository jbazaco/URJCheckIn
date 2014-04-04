from django.contrib import admin
from models import Degree, Subject, Room, UserProfile, Lesson, CheckIn, ForumComment, Timetable, LessonComment, Building
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
import datetime


########
# User #
########
admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
	model = UserProfile

class MyUserAdmin(UserAdmin):
	list_display = UserAdmin.list_display + ('profile_is_student',)
	list_filter = UserAdmin.list_filter + ('userprofile__is_student', 'userprofile__degrees')
	search_fields = UserAdmin.search_fields + ('userprofile__subjects__name',
					'userprofile__degrees__name', 'userprofile__dni')
	inlines = [UserProfileInline,]
	
	def profile_is_student(self, object):
		return object.userprofile.is_student
	profile_is_student.short_description = "es estudiante"

admin.site.register(User, MyUserAdmin)

###########
# Subject #
###########
class SubjectStateFilter(admin.SimpleListFilter):
	"""Para filtrar las asignaturas segun sean antiguas, actuales o futuras"""
	title = 'estado'
	# Parameter for the filter that will be used in the URL query.
	parameter_name = 'status'

	def lookups(self, request, model_admin):
		return (
			('old', 'Antigua'),
			('now', 'Actual'),
			('fut', 'Futura'),
		)

	def queryset(self, request, queryset):
		today = datetime.date.today()
		if self.value() == 'old':
			return queryset.filter(last_date__lt = today)
		if self.value() == 'now':
			return queryset.filter(last_date__gte = today, first_date__lte = today)
		if self.value() == 'fut':
			return queryset.filter(first_date__gt = today)

class SubjectAdmin(admin.ModelAdmin):
	fieldsets = [
		(None , {'fields': ['name', 'degrees', 'first_date', 'last_date', 'creator']}),
		('Seminario', {'fields': ['is_seminar', 'max_students', 'description'], 'classes':['collapse']}),
	 ]
	list_display = ('name', 'first_date', 'last_date', 'subject_state')
	list_filter = ['is_seminar', SubjectStateFilter, 'degrees']
	search_fields = ['name', 'degrees__name', 'userprofile__user__first_name', 
					'userprofile__user__last_name']

admin.site.register(Subject, SubjectAdmin)

############
# Building #
############
class RoomInline(admin.TabularInline):
	model = Room
	extra = 3

class BuildingAdmin(admin.ModelAdmin):
	inlines = [
		RoomInline,
	]
admin.site.register(Building, BuildingAdmin)

admin.site.register(Degree)
admin.site.register(Room)
admin.site.register(Lesson)
admin.site.register(CheckIn)
admin.site.register(ForumComment)#TODO no deberian poder poner nuevos o modificarlos, solo borrarlos
admin.site.register(Timetable)
admin.site.register(LessonComment)
