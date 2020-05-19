from django import forms
class MTurkAssignmentForm(forms.Form):
	data = forms.CharField(required=True)
	action_log = forms.CharField(required=True)
	feedback = forms.CharField(required=False)