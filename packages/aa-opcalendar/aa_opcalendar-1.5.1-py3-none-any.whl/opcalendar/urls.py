from django.urls import path

from . import views

app_name = "opcalendar"
urlpatterns = [
    path("index", views.index, name="index"),
    path("", views.CalendarView.as_view(), name="calendar"),
    path("event/new/", views.create_event, name="event_new"),
    path("add_ingame_calendar/", views.add_ingame_calendar, name="add_ingame_calendar"),
    path("event/edit/<int:pk>/", views.EventEdit.as_view(), name="event_edit"),
    path("event/<int:event_id>/details/", views.event_details, name="event-detail"),
    path(
        "ingame/event/<int:event_id>/details/",
        views.ingame_event_details,
        name="ingame-event-detail",
    ),
    path(
        "add_eventmember/<int:event_id>", views.add_eventmember, name="add_eventmember"
    ),
    path("event/<int:event_id>/remove", views.EventDeleteView, name="remove_event"),
]
