from django.contrib import admin
from .models import Event
from .models import Venue
#from django.contrib.auth.models import Group # to Remove groups from Admin panel
#from .models import MyClubUser

#admin.site.register(Event)
#admin.site.register(MyClubUser)

#admin.site.unregister(Group) # to Remove groups from Admin panel

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    ordering = ('name',) # '-name' for reverse
    search_fields = ('name', 'address')
#admin.site.register(Venue) #insted of @admin.register(Venue) (should be below class)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = (('name', 'venue'), 'event_date', 'description', 'manager', 'approved')
    list_display = ('name', 'event_date', 'venue') 
    list_filter = ('event_date', 'venue')
    ordering = ('event_date',)

# Register your models here.
