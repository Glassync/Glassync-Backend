from django import forms
from .models import Event, RecurrenceRule


class RecurrenceRuleForm(forms.ModelForm):
    class Meta:
        model = RecurrenceRule
        fields = ['type', 'interval']

    measurement_type = forms.ChoiceField(
        choices=[
            ('DAYS', 'Days'),
            ('WEEKS', 'Weeks'),
            ('MONTHS', 'Months'),
            ('YEARS', 'Years'),
        ],
        required=False,
        label='Measure Interval',
        widget=forms.Select(attrs={'style': 'display:none;'})
    )

    def clean(self):
        cleaned_data = super().clean()
        recurrence_type = cleaned_data.get('type')

        if recurrence_type == 'CUSTOM':
            interval = cleaned_data.get('interval')
            measure_type = cleaned_data.get('measurement_type')

            if not measure_type:
                raise forms.ValidationError('Please select a measure type (days, weeks, months, years).')

            if not interval or interval < 1:
                raise forms.ValidationError('Interval must be a positive number.')

            cleaned_data['interval'] = interval
            cleaned_data['measure_type'] = measure_type

        elif recurrence_type != 'CUSTOM':
            cleaned_data['measurement_type'] = 'DAYS'
            cleaned_data['interval'] = 1

        return cleaned_data


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['user', 'name', 'description', 'location', 'day', 'start_time', 'end_time', 'recurrence_rule']
        widgets = {
            'day': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'})
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        if start and end:
            if end <= start:
                raise forms.ValidationError("End time must be after start time.")

        return cleaned_data
