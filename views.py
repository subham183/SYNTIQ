import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .engine import ASTAnalyzer, LinguisticHumanizer, SubmissionTracker


def index(request):
    stats = SubmissionTracker.aggregate()
    return render(request, 'analyzer/index.html', {'stats': stats})


def dashboard(request):
    stats = SubmissionTracker.aggregate()
    return render(request, 'analyzer/dashboard.html', {'stats': stats})


@csrf_exempt
@require_http_methods(["POST"])
def analyze_code(request):
    try:
        data = json.loads(request.body)
        source = data.get('code', '').strip()
        if not source:
            return JsonResponse({'error': 'No code provided'}, status=400)

        analyzer = ASTAnalyzer(source)
        result = analyzer.analyze()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def humanize_text(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)

        humanizer = LinguisticHumanizer(text)
        result = humanizer.analyze_and_transform()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_dual(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        text = data.get('text', '').strip()

        code_result = {}
        text_result = {}

        if code:
            analyzer = ASTAnalyzer(code)
            code_result = analyzer.analyze()

        if text:
            humanizer = LinguisticHumanizer(text)
            text_result = humanizer.analyze_and_transform()

        if code_result or text_result:
            submission_id = SubmissionTracker.record(
                code_result or {'metrics': {}, 'hazards': [], 'grade': '?'},
                text_result or {'metrics': {}}
            )
        else:
            return JsonResponse({'error': 'Provide code or text'}, status=400)

        return JsonResponse({
            'submission_id': submission_id,
            'code_analysis': code_result,
            'text_humanization': text_result,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_stats(request):
    return JsonResponse(SubmissionTracker.aggregate())
