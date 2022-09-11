from typing import Dict, Tuple

from marshmallow import Schema, ValidationError


class BaseSchema(Schema):
    def verify(self, form: Dict, partial=False) -> Tuple[Dict, Dict]:
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