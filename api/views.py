from .models import Report
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import generate_report

@csrf_exempt
def trigger_report(request):
    report = Report.objects.create()
    generate_report.delay(report.id)
    return JsonResponse({'report_id': report.id}, status=202)

def get_report(request):
    report_id = request.GET.get('report_id', None)
    if not report_id:
        return JsonResponse({'error': 'Report ID is required.'}, status=400)
    
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return JsonResponse({'error': 'Report not found.'}, status=404)
    
    if report.status == 'Done':
        file = "http://localhost/static/reports/" + report_id + ".csv"
        return JsonResponse({'status': 'Done', 'report_data': file}, status=200)
    return JsonResponse({'status': report.status})
