from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event, Venue
from django.contrib.auth.models import User

from .forms import VenueForm, EventForm, EventFormAdmin
from django.http import HttpResponse
import csv
# PDF imports
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from django.core.paginator import Paginator

from django.contrib import messages

def my_events(request):
    if request.user.is_authenticated:
        me = request.user.id
        events = Event.objects.filter(attendees=me)
        return render(request, 'events/my_events.html', {
            'events': events,
        })
    else:
        messages.success(request, 'Login to wiev this page')
        return redirect('login')

#Generate PDF
def venue_pdf(request):
    #create Bytestream buffer
    buf = io.BytesIO()
    #create canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    #ctreate a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont('Helvetica', 14)

    venues = Venue.objects.all()

    lines = []

    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append('======================')

    for line in lines:
        textob.textLine(line)

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='venues.pdf')
    
#Generate csv
def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Contnt-Disposition'] = 'attachment; filename=venues.csv'
    #create a CSV WRITER
    writer = csv.writer(response)
    # Designate the model
    venues = Venue.objects.all()
    #add columns headings to the csv file
    writer.writerow(['Venue name', 'Address', 'Zip code', 'Phone', 'Web Address', 'Email'])
    for venue in venues:
        writer.writerow([venue, venue.address, venue.zip_code, venue.phone, venue.web, venue.email_address])
    return response

#generate text file venue list
def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Contnt-Disposition'] = 'attachment; filename=venues.txt'
    # Designate the model
    venues = Venue.objects.all()
    lines = []
    for venue in venues:
        lines.append(f'{venue}\n {venue.address}\n {venue.zip_code}\n {venue.phone}\n {venue.web}\n {venue.email_address}\n\n\n')
    #write to text file
    response.writelines(lines)
    return response

def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')

def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager:
        event.delete()
        messages.success(request, 'Event was succesfully deleted')
        return redirect('list-events')
    else:
        messages.success(request, 'You can not delete events of other managers')
        return redirect('list-events')

def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('list-events')
    return render(request, 'events/update_event.html', { 
        "event": event,
        'form': form,
    })

def add_event(request):
    submitted = False
    if request.method == 'POST':
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventForm(request.POST)
            
            
            if form.is_valid():
                event = form.save(commit=False) # make a form but dont save
                event.manager = request.user # logged in user
                event.save()
                return HttpResponseRedirect('/add_event?submitted=True')
    else:
        # no submit
        if request.user.is_superuser:
            form = EventFormAdmin
        else:
            form = EventForm
        if "submitted" in request.GET:
            submitted = True
    return render(request, 'events/add_event.html', {'form': form, 'submitted': submitted})

def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')
    return render(request, 'events/update_venue.html', { 
        "venue": venue,
        'form': form,
    })
    
def search_events(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        events = Event.objects.filter(name__contains=searched)
        return render(request, 'events/search_events.html', {
                'searched': searched,
                'events': events,
            })
    else:
        return render(request, 'events/search_events.html', {})

def search_venues(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        venues = Venue.objects.filter(name__contains=searched)
        return render(request, 'events/search_venues.html', {
                'searched': searched,
                'venues': venues,
            })
    else:
        return render(request, 'events/search_venues.html', {})

def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)
    return render(request, 'events/show_venue.html', {
        "venue": venue,
        "venue_owner": venue_owner,
    })

def list_venues(request):
    #venue_list = Venue.objects.all()

    # set pagination
    p = Paginator(Venue.objects.all().order_by('name'), 3)
    page = request.GET.get('page')
    venues = p.get_page(page)
    nums = "a" * venues.paginator.num_pages
    return render(request, 'events/venues.html', {
        #"venue_list": venue_list,
        'venues': venues,
        'nums': nums,
    })

def add_venue(request):
    submitted = False
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False) # make a form but dont save
            venue.owner = request.user.id # logged in user
            venue.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if "submitted" in request.GET:
            submitted = True
    return render(request, 'events/add_venue.html', {'form': form, 'submitted': submitted})

def all_events(request):
    event_list = Event.objects.all().order_by('event_date')
    return render(request, 'events/event_list.html', {
        "event_list": event_list
    })

def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = "Artem"
    month = month.capitalize()
    #convert month from name to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)
    #get current year
    now = datetime.now()
    current_year = now.year
    #get current time
    time = now.strftime('%I:%M %p')
    #create calendar
    cal = HTMLCalendar().formatmonth(year, month_number)
    return render(request, 'events/home.html', {
        'name': name,
        'year': year,
        'month': month,
        'month_number': month_number,
        'cal': cal,
        "current_year": current_year,
        'time': time,
    })

# Create your views here.
