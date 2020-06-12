from django import forms

state_Choices = (
        ('LA', 'Lagos State'),
        ('OG', 'Ogun State'),
        ('OY', 'Oyo State'),
    )
Payment_Choices = (
    ('S', 'Debit Card'),
    ('P', 'Pay on Delivery')
)
class CheckOutForm(forms.Form):
    state = forms.ChoiceField(widget=forms.Select(attrs={'Placeholder': 'Select Hall', 'class': 'form-control', 'id': 'address'}), choices=state_Choices, required=True)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    Payment_option = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'custom-control-input', 'size': 100}), choices=Payment_Choices, required=True)
