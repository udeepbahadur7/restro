import colorsys
import json
import random
from collections import defaultdict

from actstream.models import Action
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import SuspiciousOperation
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay, ExtractHour, TruncDay
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from dashboard.forms import DashboardDateFilterForm
from wifiportal.models import Organization, Customer


def get_random_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
    return 'rgb({}, {}, {})'.format(r, g, b)


def get_users_timezone(user):
    if (hasattr(user, 'organization')):
        return user.organization.timezone
    return 'Asia/Kathmandu'


@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_date_range_form(self):
        return DashboardDateFilterForm(self.request.GET)

    def get_date_range(self, date_form):
        from_date, to_date = None, None
        if date_form.is_valid():
            from_date = date_form.cleaned_data['timestamp_from']
            to_date = date_form.cleaned_data['timestamp_to']

        present_time = timezone.localtime()
        present_time = present_time.replace(hour=0, minute=0, second=0, microsecond=0)

        time_interval = timezone.timedelta(days=30)

        from_date = from_date or present_time - time_interval
        to_date     = to_date or present_time + timezone.timedelta(days=1)

        return from_date, to_date

    def get_context_data(self, **kwargs):
        timezone.activate(get_users_timezone(self.request.user))
        context = admin.site.each_context(self.request)

        date_range_form = self.get_date_range_form()
        from_time, to_time = self.get_date_range(date_range_form)

        context.update(dict(
            to_time=to_time,
            from_time=from_time,
            date_range_form=date_range_form
        ))

        new_user_datasets = self.get_new_user_data(from_time, to_time, self.request.user)

        active_user_datasets = self.get_active_user_data(from_time, to_time, self.request.user)
        labels = [label.strftime("%Y-%m-%d") for label in self.get_time_range(from_time, to_time, timezone.timedelta(days=1))]

        time_heat_map_datasets = self.get_users_by_time(from_time, to_time, self.request.user)
        time_heat_map_labels = range(0,24)

        context.update(dict(
            new_user_datasets=json.dumps(new_user_datasets),
            new_user_x_axis_labels=json.dumps(labels),
            active_user_datasets=json.dumps(active_user_datasets),
            active_user_x_axis_labels=json.dumps(labels),
            time_heat_map_datasets=json.dumps(time_heat_map_datasets),
            time_heat_map_labels=json.dumps(time_heat_map_labels),
        ))

        most_active_day, count = self.get_most_active_day(time_heat_map_datasets)
        new_user_count = self.get_total_new_user_count(new_user_datasets)
        total_session_count = self.get_total_active_sessions_count(active_user_datasets)
        most_active_hour = self.get_most_active_hour(time_heat_map_datasets)
        context.update(dict(
            most_active_day=most_active_day,
            new_user_count=new_user_count,
            total_session_count=total_session_count,
            most_active_hour=most_active_hour,
        ))
        return context

    def get_users_by_time(self, from_date, to_date, user):
        actions_filters = dict(
            timestamp__gt=from_date,
            timestamp__lt=to_date,
            verb='logged in'
        )
        if not user.is_superuser:
            if not hasattr(user, 'organization'):
                raise SuspiciousOperation
            actions_filters['target_object_id'] = user.organization.id

        dataset = Action.objects.filter(**actions_filters
        ).annotate(weekday=ExtractWeekDay('timestamp'), hour=ExtractHour('timestamp')
        ).values('weekday', 'hour'
        ).annotate(count=Count('hour')
        ).values('weekday', 'hour', 'count'
        ).order_by('weekday')

        cluster_map = defaultdict(list)
        for data_item in dataset:
            cluster_map[data_item['weekday']].append(data_item)

        def dataset_factory(week_day, daydata_dict):
            if not daydata_dict:
                return dict()

            daydata_map = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            label = daydata_dict[0]['weekday']
            label = daydata_map[label-1]
            date_count_tuple = [(daydata['hour'], daydata['count']) for daydata in daydata_dict]
            date_count_tuple = self.fillin_missing_hour_data(date_count_tuple)

            return dict(
                label=label,
                data=[date_count[1] for date_count in date_count_tuple],
                fill=False,
                borderColor=get_random_color()
                # lineTension=0.1
            )

        return [dataset_factory(*item) for item in cluster_map.iteritems()]

    def get_most_active_day(self, time_heat_map_datasets):
        if not time_heat_map_datasets:
            return 'NA', 0
        most_active_day_data = max(time_heat_map_datasets, key=lambda dataset: sum(dataset['data']))
        return most_active_day_data['label'], sum(most_active_day_data['data'])

    def get_total_new_user_count(self, new_user_datasets):
        return reduce(lambda a,b: (a + sum(b['data'])), new_user_datasets, 0)

    def get_total_active_sessions_count(self, active_user_datasets):
        return reduce(lambda a, b: (a + sum(b['data'])), active_user_datasets, 0)

    def get_most_active_hour(self, time_heat_map_datasets):
        if not time_heat_map_datasets:
            return 'NA'
        count_data = map(lambda item: item['data'], time_heat_map_datasets)
        summed_data = [sum(x) for x in zip(*count_data)]
        hour_index = summed_data.index(max(summed_data))
        hour = hour_index % 12  or 12
        is_pm = hour_index / 12
        am_pm = ' pm' if is_pm else ' am'
        return unicode(hour) + am_pm

    def get_active_user_data(self, from_date, to_date, user):
        action_filters = dict(
            timestamp__gt=from_date,
            timestamp__lt=to_date,
            verb='logged in'
        )
        if not user.is_superuser:
            if not hasattr(user, 'organization'):
                raise SuspiciousOperation
            action_filters['target_object_id'] = user.organization.id

        dataset = Action.objects.filter(**action_filters
        ).annotate(day=TruncDay('timestamp')
        ).values('day', 'target_object_id'
        ).annotate(count=Count('day')
        ).values('day', 'count', 'target_object_id'
        ).order_by('day')

        cluster_map = defaultdict(list)
        for data_item in dataset:
            cluster_map[data_item['target_object_id']].append(data_item)

        organizations = Organization.objects.filter(id__in=cluster_map.keys())
        organization_map = dict([(str(item.id), item.name) for item in organizations])

        def dataset_factory(organization_id, daydata_dict):
            if not daydata_dict:
                return dict()

            target_object_id = daydata_dict[0]['target_object_id']
            label = organization_map.get(target_object_id, target_object_id)
            date_count_tuple = [(str(daydata['day']), daydata['count']) for daydata in daydata_dict]
            date_count_tuple = self.fillin_missing_date_data(date_count_tuple, from_date, to_date)

            return dict(
                label=label,
                data=[date_count[1] for date_count in date_count_tuple],
                fill=False,
                borderColor=get_random_color()
                # lineTension=0.1
            )

        return [dataset_factory(*item) for item in cluster_map.iteritems()]

    def get_new_user_data(self, from_date, to_date, user):
        dataset = Customer.objects.get_new_customer_counts(from_date, to_date, user)

        cluster_map = defaultdict(list)

        for data_item in dataset:
            cluster_map[data_item['organization_id']].append(data_item)

        def dataset_factory(organization_id, daydata_dict):
            if not daydata_dict:
                return dict()

            label = daydata_dict[0]['organization__name']
            date_count_tuple = [(str(item['day']), item['count']) for item in daydata_dict]
            date_count_tuple = self.fillin_missing_date_data(date_count_tuple, from_date, to_date)

            return dict(
                label=label,
                data=[item[1] for item in date_count_tuple],
                fill=False,
                borderColor=get_random_color()
                # lineTension=0.1
            )

        return [dataset_factory(*item) for item in cluster_map.iteritems()]

    def fillin_missing_hour_data(self, hour_count_tuple):
        hour_count_map = dict(hour_count_tuple)

        for hour in xrange(0, 24):
            yield (hour, hour_count_map.get(hour, 0))

    def fillin_missing_date_data(self, date_count_tuple, from_date, to_date):
        date_count_map = dict(date_count_tuple)
        time_delta = timezone.timedelta(days=1)

        for temp_date in self.get_time_range(from_date, to_date, time_delta):
            yield (temp_date, date_count_map.get(str(temp_date), 0))

    def get_time_range(self, from_date, to_date, time_delta):
        if from_date > to_date:
            return

        temp_date = from_date
        while temp_date < to_date:
            yield temp_date
            temp_date += time_delta
