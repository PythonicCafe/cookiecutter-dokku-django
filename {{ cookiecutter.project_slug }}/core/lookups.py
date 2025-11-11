from django.core.exceptions import FieldError
from django.db import models


class ChoiceDisplayLookup(models.Lookup):
    lookup_name = "display"
    _cache = {}

    def get_prep_lookup(self):
        field = self.lhs.output_field

        if not hasattr(field, "choices") or not field.choices:
            raise FieldError("Field %s does not have choices defined" % repr(field.name))

        if field not in ChoiceDisplayLookup._cache:
            ChoiceDisplayLookup._cache[field] = {display: value for value, display in field.choices}
        reverse_choices = ChoiceDisplayLookup._cache[field]

        display_value = self.rhs
        if display_value not in reverse_choices:
            raise ValueError("Display value %s not found in field %s choices" % (display_value, field.name))
        return reverse_choices[display_value]

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f"{lhs} = {rhs}", lhs_params + rhs_params


models.SmallIntegerField.register_lookup(ChoiceDisplayLookup)
