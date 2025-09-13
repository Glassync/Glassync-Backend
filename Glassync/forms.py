from django import forms
from .models import Event, RecurrenceRule


class RecurrenceRuleForm(forms.ModelForm):
    class Meta:
        model = RecurrenceRule
        fields = ['type', 'interval']

    def clean(self):
        cleaned_data = super().clean()
        type_value = cleaned_data.get('type')

        if type_value == "Daily":
            cleaned_data['type'] = RecurrenceRule.RecurrenceType.DAYS
            cleaned_data['interval'] = 1
        elif type_value == "Weekly":
            cleaned_data['type'] = RecurrenceRule.RecurrenceType.WEEKS
            cleaned_data['interval'] = 1
        elif type_value == "Monthly":
            cleaned_data['type'] = RecurrenceRule.RecurrenceType.MONTHS
            cleaned_data['interval'] = 1
        elif type_value == "Yearly":
            cleaned_data['type'] = RecurrenceRule.RecurrenceType.YEARS
            cleaned_data['interval'] = 1
        elif type_value == "Custom":
            pass
        else:
            print("[ERROR] Wrong RecurrenceRule Type")
            raise forms.ValidationError("Invalid recurrence type.")

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
