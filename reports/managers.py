from django.db import models


class KindInterestRequestMaterialQuerySet(models.QuerySet):
    def request_pmnh(self):
        return self.filter(kind=self.model.REQUEST)

    def interest_pmnh(self):
        return self.filter(kind=self.model.INTEREST)
