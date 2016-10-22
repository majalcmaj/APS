from random import randint
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView


class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels."""
        return ["1", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2"]

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 20, 44, 95, 20, 44, 95, 20],
                [41, 92, 18, 3, 73, 87, 92, 44, 95, 20, 44, 95, 20],
                [87, 21, 94, 3, 90, 13, 65, 44, 95, 20, 44, 95, 20]]


line_chart = TemplateView.as_view(template_name='line_chart.html')
line_chart_json = LineChartJSONView.as_view()