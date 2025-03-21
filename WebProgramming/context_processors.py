from datetime import datetime

def current_time(request):
    return {'current_time': datetime.now().strftime("%b %d • %H:%M")}