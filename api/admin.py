from django.contrib import admin
from .models import Places, SubPlaces
from django.utils.html import format_html

class PlacesAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_description', 'type', 'address')
    
    def formatted_description(self, obj):
        return format_html("<pre>{}</pre>", obj.description)
    
    formatted_description.short_description = 'Description'

class SubPlacesAdmin(admin.ModelAdmin):
    list_display = ('name', 'place', 'formatted_description', 'type')
    
    def formatted_description(self, obj):
        return format_html("<pre>{}</pre>", obj.description)
    
    formatted_description.short_description = 'Description'

admin.site.register(Places, PlacesAdmin)
admin.site.register(SubPlaces, SubPlacesAdmin)
