from django.contrib.gis import forms
from django.utils.text import slugify

from walks.models import Walk, Attribute


class ResponsiveMapWidget(forms.OpenLayersWidget):
    template_name = "walks/widgets/responsive_map.html"
    default_lon = -2.2503
    default_lat = 51.8766
    default_zoom = 12

    def __init__(self, attrs=None):
        super().__init__()
        for key in ("default_lon", "default_lat", "default_zoom"):
            self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)

    class Media:
        extend = False
        css = {
            "all": (
                "https://cdnjs.cloudflare.com/ajax/libs/ol3/4.6.5/ol.css",
                "gis/css/ol3.css",
            )
        }
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/ol3/4.6.5/ol.js",
            "core/js/OLMapWidget.js",
        )


class SearchForm(forms.Form):
    postcode = forms.CharField(
        max_length=50, required=False, help_text="Enter a Post code to search from"
    )
    use_current_location = forms.BooleanField(initial=False, required=False)
    search_radius = forms.IntegerField(
        min_value=0, max_value=200, help_text="Search distance (Miles)"
    )
    maximum_length = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=250,
        help_text="Maximum walk length (Miles)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for attribute in Attribute.objects.all():
            self.fields[attribute.attribute] = forms.BooleanField(
                initial=False, required=False
            )

    def clean(self):
        if (
            not self.cleaned_data["postcode"]
            and not self.cleaned_data["use_current_location"]
        ):
            raise forms.ValidationError(
                "You must enter a postcode or location or use your current location"
            )


class WalkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        submitter = kwargs.pop("submitter")
        super().__init__(*args, **kwargs)
        self.fields["submitter"].initial = submitter

        self.fields["attributes"] = forms.ModelMultipleChoiceField(
            queryset=Attribute.objects.all(),
            widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        )

        if self.instance.pk:
            self.fields["route"].widget.attrs.update({"default_zoom": 13})

    def clean(self):
        """
        check the walk route was entered
        """
        if "route" not in self.cleaned_data:
            raise forms.ValidationError("Please enter the walk route using the map")

        self.cleaned_data["slug"] = slugify(self.cleaned_data["name"])

        return self.cleaned_data

    class Meta:
        model = Walk
        fields = ("name", "description", "route", "attributes", "submitter")
        widgets = {
            "route": ResponsiveMapWidget(
                attrs={"default_zoom": 10, "modifiable": True}
            ),
            "submitter": forms.HiddenInput(),
        }
        help_texts = {
            "name": "A descriptive name for this walk",
            "description": "Describe the walk in as much detail as you can.\n"
            "Include points of interest and instructions",
            "route": "Use the map to enter the walk route.\n"
            "Click on the map to start drawing the route and double click to end.\n"
            "Use the Esc, Delete or Backspace Key to remove only the last point.\n"
            "Use the button to remove all points.",
        }
        error_messages = {
            "route": {"required": "Please enter the walk route using the map"}
        }


class ReadOnlyWalkRouteForm(forms.Form):
    """
    Readonly map widget for displaying walk
    """

    route = forms.LineStringField(
        widget=ResponsiveMapWidget(attrs={"default_zoom": 16, "modifiable": False}),
        label="",
        disabled=True,
    )
