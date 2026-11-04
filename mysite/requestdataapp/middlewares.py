import time

from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render


class ThrottlingMiddleware:
    """
    Rejects a request with 429 if the previous request
    from the same IP came less than THROTTLING_INTERVAL seconds ago.
    Requests answered with a redirect are not counted.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.interval = getattr(settings, "THROTTLING_INTERVAL", 1.0)
        self.last_request_time: dict[str, float] = {}

    def __call__(self, request: HttpRequest):
        ip = request.META.get("REMOTE_ADDR")
        now = time.monotonic()
        last_time = self.last_request_time.get(ip)

        if last_time is not None and now - last_time < self.interval:
            context = {
                "wait_seconds": self.interval - (now - last_time),
            }
            return render(request, "requestdataapp/throttled.html", context=context, status=429)

        self.last_request_time[ip] = now
        response = self.get_response(request)

        # The browser follows a redirect at once, without the user doing anything,
        # so a redirecting request must not make the next one look too frequent.
        if response.status_code in (301, 302, 303, 307, 308):
            self.last_request_time.pop(ip, None)

        return response
