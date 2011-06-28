from django.contrib.auth.models import User
from django.db.models import Sum

from ...restful import (ModelRestView, RestView, RestResult, restful_api,
        restful_modelapi, UrlMapping)
from simplified import StatConfig




@restful_api
class RestPeriodPoints(RestView):

    def crud_read(self, request, id):
        dataset = User.objects.filter(
            candidate__assignment_group__parentnode__parentnode__id=id).distinct()
        dataset = dataset.annotate(
                sumperiod=Sum('candidate__assignment_group__scaled_points'))
        data = dataset.values('username', 'sumperiod')
        return RestResult(dict(items=data))


@restful_modelapi
class RestStatConfig(ModelRestView):
    class Meta:
        simplified = StatConfig
        urlmap = {'periodpoints_url': UrlMapping(RestPeriodPoints, 'period__id')}