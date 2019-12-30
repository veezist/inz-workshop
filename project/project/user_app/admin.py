from django.contrib import admin
from user_app.models import Car,User, CarInstance

# class UserAdmin(admin.ModelAdmin):

#     fieldsets = [
#         ("Title/date", {'fields': ["tutorial_title", "tutorial_published"]}),
#         ("URL", {'fields': ["tutorial_slug"]}),
#         ("Series", {'fields': ["tutorial_series"]}),
#         ("Content", {"fields": ["tutorial_content"]})
#     ]
class CarInline(admin.TabularInline):
    model = CarInstance

class UserAdmin(admin.ModelAdmin):
   
    inlines = [
        CarInline
    ]

# class UserAdmin(admin.ModelAdmin):
#     exclude = ('email')


# Register your models here.
admin.site.register(Car)
admin.site.register(CarInstance)
admin.site.register(User,UserAdmin)