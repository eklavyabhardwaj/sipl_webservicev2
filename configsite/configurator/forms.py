# configurator/forms.py
from django import forms
from django.core.exceptions import ValidationError
import re
from .models import ProductGroup, Question,  Choice

class ContactForm(forms.Form):
    name = forms.CharField(max_length=140)
    email = forms.EmailField()
    phone = forms.CharField(max_length=40, required=False)
    subject = forms.CharField(max_length=180, required=False)
    message = forms.CharField(widget=forms.Textarea)

EMAIL_SAFE = re.compile(r'(?u)[^-\w.@]')

def keep_at_secure_filename(s: str) -> str:
    s = (s or "").strip().replace(" ", "_")
    return EMAIL_SAFE.sub("", s)

class JobApplicationForm(forms.Form):
    applicant_name = forms.CharField(max_length=200)
    job_title = forms.CharField(max_length=200, required=False)
    designation = forms.CharField(max_length=200, required=False)
    email_id = forms.EmailField()
    phone_number = forms.CharField(max_length=50, required=False)
    country = forms.CharField(max_length=120, required=False)
    cover_letter = forms.CharField(widget=forms.Textarea, required=False)
    lower_range = forms.CharField(required=False)
    upper_range = forms.CharField(required=False)
    resume_link = forms.URLField(required=False)
    SOURCE_CHOICES = [
        ("Campaign", "Campaign"),
        ("Employee Referral", "Employee Referral"),
        ("Walk In", "Walk In"),
        ("Website Listing", "Website Listing"),
    ]
    source = forms.ChoiceField(choices=SOURCE_CHOICES)
    resume_attachment = forms.FileField(required=False)

    def clean_resume_attachment(self):
        f = self.cleaned_data.get("resume_attachment")
        if not f:
            return f
        name = (f.name or "")
        if "." not in name:
            raise ValidationError("Invalid file name.")
        ext = name.rsplit(".", 1)[1].lower()
        if ext != "pdf":
            raise ValidationError("Invalid file format! Please upload a PDF.")
        if f.size > 8 * 1024 * 1024:
            raise ValidationError("File too large (max 8MB).")
        return f


class QuizForm(forms.Form):
    def __init__(self, group: ProductGroup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group

        # Build queryset with deps ready
        qs = (
            group.questions.filter(is_active=True)
            .order_by("order", "id")
            .prefetch_related("choices", "trigger_choices", "depends_on")
        )

        id_to_question = {}

        # -------------------------
        # PASS 1: build the fields
        # -------------------------
        for q in qs:
            choices_qs = q.choices.filter(is_active=True).order_by("order", "id")

            if getattr(Question, "INPUT_MULTI", None) and q.input_type == Question.INPUT_MULTI:
                field = forms.ModelMultipleChoiceField(
                    label=q.text,
                    queryset=choices_qs,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,  # we'll set based on visibility in pass 2
                )
                field.widget.attrs["data_multi"] = "1"
            else:
                field = forms.ModelChoiceField(
                    label=q.text,
                    queryset=choices_qs,
                    widget=forms.RadioSelect,
                    required=False,  # we'll set based on visibility in pass 2
                    empty_label=None,
                )
                field.widget.attrs["data_multi"] = "0"

            # <-- YOU ADD THE DEPENDENCY ATTRS **HERE**, inside the loop
            if getattr(q, "depends_on_id", None):
                parent_field_name = f"q_{q.depends_on_id}"
                parent_panel_id = f"wrap_{parent_field_name}"

                # HTML data-* (hyphen) for JS
                field.widget.attrs["data-depends-on"] = parent_panel_id
                trig_ids = list(q.trigger_choices.values_list("id", flat=True))
                field.widget.attrs["data-trigger-choices"] = ",".join(map(str, trig_ids)) if trig_ids else ""

                # Underscore twins for Django template access
                field.widget.attrs["data_depends_on"] = parent_panel_id
                field.widget.attrs["data_trigger_choices"] = field.widget.attrs["data-trigger-choices"]

            self.fields[f"q_{q.id}"] = field
            id_to_question[q.id] = q

        # -------------------------
        # PASS 2: compute visibility
        # -------------------------
        selected_choice_ids = self._selected_choice_ids(id_to_question)

        for qid, q in id_to_question.items():
            visible = self._is_triggered_by(q, selected_choice_ids)
            f = self.fields[f"q_{qid}"]

            # Provide both hyphen and underscore variants for the template/JS
            f.widget.attrs["data-visible"] = "1" if visible else "0"
            f.widget.attrs["data_visible"] = f.widget.attrs["data-visible"]

            # Only visible required questions are actually required
            f.required = bool(visible and q.is_required)

    # Helpers --------------------------------------------------------------

    def _selected_choice_ids(self, id_to_question) -> set[int]:
        """
        From incoming GET/POST, figure out which choices are selected.
        Works for both single and multi fields.
        """
        data = self.data if self.is_bound else {}
        out = set()

        for qid in id_to_question:
            name = f"q_{qid}"
            if not data:
                continue

            # QueryDict has getlist; plain dict doesn't
            vals = data.getlist(name) if hasattr(data, "getlist") else data.get(name)

            if not vals:
                continue

            if isinstance(vals, (list, tuple)):
                for v in vals:
                    try:
                        out.add(int(v))
                    except Exception:
                        pass
            else:
                try:
                    out.add(int(vals))
                except Exception:
                    pass
        return out

    def _is_triggered_by(self, q: Question, selected_choice_ids: set[int]) -> bool:
        """
        True if question q should be visible given selected choices.
        - No dependency -> visible
        - Dependency with trigger choices -> visible if any of those are selected
        - Dependency without trigger choices -> visible if parent has any selection
        """
        if not getattr(q, "depends_on_id", None):
            return True

        trig_ids = set(q.trigger_choices.values_list("id", flat=True))
        if trig_ids:
            return bool(trig_ids & selected_choice_ids)

        # No explicit trigger list: any selection in parent reveals it
        parent_choice_ids = set(
            Choice.objects.filter(question_id=q.depends_on_id).values_list("id", flat=True)
        )
        return bool(parent_choice_ids & selected_choice_ids)




class ParticipantForm(forms.Form):
    name = forms.CharField(max_length=140, label="Full name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=40, label="Phone number")
    designation = forms.CharField(max_length=140, label="Designation (optional)", required=False)
    company = forms.CharField(max_length=180, label="Company (optional)", required=False)







# forms.py
from django import forms
from django.utils.text import slugify
from .models import Item

class VariantFacetForm(forms.Form):
    """
    Builds checkbox fields from ItemVariantSpec values of an item's active variants.
    For each spec label, we create a multi-select of unique values (value+unit).
    """
    def __init__(self, item: Item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item

        variants = (item.variants
                        .filter(is_active=True)
                        .prefetch_related("specs"))

        # label -> set of (value, unit)
        facets = {}
        for v in variants:
            for s in v.specs.all():
                label = (s.label or "").strip()
                value = (s.value or "").strip()
                unit  = (s.unit or "").strip()
                if not label or not value:
                    continue
                facets.setdefault(label, set()).add((value, unit))

        for label, vu_set in sorted(facets.items(), key=lambda kv: kv[0].lower()):
            # store value as "value||unit" so we can split cleanly later
            choices = []
            for (val, unit) in sorted(vu_set, key=lambda t: (t[0].lower(), t[1].lower())):
                stored = f"{val}||{unit}"
                display = f"{val} {unit}".strip()
                choices.append((stored, display))

            field_name = f"facet__{slugify(label)}"
            self.fields[field_name] = forms.MultipleChoiceField(
                label=label,
                choices=choices,
                required=False,
                widget=forms.CheckboxSelectMultiple,
                help_text="Leave empty for any"
            )

    def selected_facets(self):
        """
        Returns: { label_slug: [(value, unit), ...], ... }
        """
        out = {}
        for name in self.fields:
            if not name.startswith("facet__"):
                continue
            tokens = self.cleaned_data.get(name) or []
            pairs = []
            for token in tokens:
                val, unit = token.split("||", 1)
                pairs.append((val, unit))
            out[name[len("facet__"):]] = pairs
        return out