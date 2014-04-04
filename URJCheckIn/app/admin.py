from django.contrib import admin
from models import Degree, Subject, Room, UserProfile, Lesson, CheckIn, ForumComment, Timetable, LessonComment, Building
import datetime

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
		('Seminario', {'fields': ['is_seminar', 'max_students', 'description']}),
	 ]
	list_display = ('name', 'first_date', 'last_date', 'subject_state')
	list_filter = ['is_seminar', SubjectStateFilter]
	search_fields = ['name', 'degrees__name', 'userprofile__user__first_name', 
					'userprofile__user__last_name']

class RoomInline(admin.TabularInline):
	model = Room
	extra = 3

class BuildingAdmin(admin.ModelAdmin):
	inlines = [
		RoomInline,
	]

admin.site.register(Degree)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Room)
admin.site.register(UserProfile)
admin.site.register(Lesson)
admin.site.register(CheckIn)
admin.site.register(ForumComment)#TODO no deberian poder poner nuevos o modificarlos, solo borrarlos
admin.site.register(Timetable)
admin.site.register(LessonComment)
admin.site.register(Building, BuildingAdmin)
