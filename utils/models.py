from django.db import models
from utils.pxfilter import XssHtml


class RichTextField(models.TextField):
    def get_prep_value(self, value):
        with XssHtml() as parser:
            return parser.clean(value or "")
