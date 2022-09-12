from typing import Dict, Tuple

from marshmallow import Schema, ValidationError


class BaseSchema(Schema):
    """Base schema"""
    def verify(self, form: Dict, partial=False) -> Tuple[Dict, Dict]:
        """Verify if the given form data is correct
        Parameters
        ---
        form: Data passed in the http request
        partial: Indicate if the fields of the form must match exactly or partially

        Return: The formatted data along with the errors
        """
        data = {}        
        errs = {}
        try:
            data = self.load(form, partial=partial)
        except ValidationError as e:
            errs['message'] = "Validation error"
            errs['fields'] = []

            for field, err in e.messages.items():
                if isinstance(err, dict):
                    errs['fields'].append({field: err['message']})
                else:
                    errs['fields'].append({field: err[0]})

        return data, errs