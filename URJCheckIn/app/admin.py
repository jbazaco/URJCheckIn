from django.contrib import admin
from models import Degree, Subject, Room, UserProfile, Lesson, CheckIn, ForumComment, Timetable, LessonComment, Building
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
import datetime
from django.utils import timezone

class TimeStateFilter(admin.SimpleListFilter):
	"""Para filtrar un modelo segun su momento de inicio y fin, clasificando los objectos en 
		antiguos, actuales o futuros"""
	title = 'estado'
	# Parameter for the filter that will be used in the URL query.
	parameter_name = 'status'

	def lookups(self, request, model_admin):
		return (
			('old', 'Anterior'),
			('now', 'Actual'),
			('fut', 'Futuro'),
		)

	class Meta:
		abstract = True

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
	inlines = [
		UserProfileInline,
	]
	
	def profile_is_student(self, object):
		return object.userprofile.is_student
	profile_is_student.short_description = "es estudiante"

admin.site.register(User, MyUserAdmin)

###########
# Subject #
###########
class SubjectStateFilter(TimeStateFilter):
	"""Para filtrar las asignaturas segun sean antiguas, actuales o futuras"""
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
		(None , {'fields': ('name', 'degrees', 'first_date', 'last_date', 'creator')}),
		('Seminario', {'fields': ('is_seminar', 'max_students', 'description'), 'classes':['collapse']}),
	 ]
	list_display = ('name', 'first_date', 'last_date', 'subject_state')
	list_filter = ('is_seminar', SubjectStateFilter, 'degrees')
	search_fields = ('name', 'degrees__name', 'userprofile__user__first_name', 
					'userprofile__user__last_name')

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

##########
# Degree #
##########
class DegreeAdmin(admin.ModelAdmin):
	list_display = ('name', 'code')
	search_fields = ('name', 'code')
admin.site.register(Degree, DegreeAdmin)

###########
# CheckIn #
###########
class CheckInAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'user',)
	search_fields = ('lesson__subject__name', 'lesson__subject__degrees__name',
			'lesson__subject__degrees__code', 'user__first_name', 'user__last_name')
	
admin.site.register(CheckIn, CheckInAdmin)

##########
# Lesson #
##########
class LessonStateFilter(TimeStateFilter):
	"""Para filtrar las clases segun sean antiguas, actuales o futuras"""
	def queryset(self, request, queryset):
		now = timezone.now()
		if self.value() == 'old':
			return queryset.filter(end_time__lt = now)
		if self.value() == 'now':
			return queryset.filter(end_time__gte = now, start_time__lte = now)
		if self.value() == 'fut':
			return queryset.filter(start_time__gt = now)

class LessonAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'start_time', 'end_time', 'done', 'is_extra')
	list_filter = ('done', 'is_extra', LessonStateFilter)
	search_fields = ('subject__name', 'subject__degrees__name', 'subject__degrees__code')

admin.site.register(Lesson, LessonAdmin)

################
# ForumComment #
################
class CommentAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'date', 'user')
	list_filter = ('date',)
	search_fields = ('comment', 'user__first_name', 'user__last_name', 'user__username')

	def has_add_permission(self, request):
		return False

admin.site.register(ForumComment, CommentAdmin)

#################
# LessonComment #
#################
class LessonCommentAdmin(CommentAdmin):
	list_display = CommentAdmin.list_display + ('lesson',)
	search_fields = CommentAdmin.search_fields + ('lesson__subject__name',)

admin.site.register(LessonComment, LessonCommentAdmin)

#############
# Timetable #
#############
class TimetableAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'subject', 'room', 'day', 'start_time', 'end_time')
	list_filter = ('day',)
	search_fields = ('subject__name', 'subject__degrees__name', 'subject__degrees__code')

admin.site.register(Timetable, TimetableAdmin)

admin.site.register(Room)

