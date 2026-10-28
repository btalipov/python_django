from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

MAX_UPLOAD_SIZE = 1024 * 1024  # 1 MB


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    context = {
        "max_size_mb": MAX_UPLOAD_SIZE // (1024 * 1024),
    }
    if request.method == "POST" and request.FILES.get("myfile"):
        myfile = request.FILES["myfile"]
        if myfile.size > MAX_UPLOAD_SIZE:
            context["error"] = (
                f"File {myfile.name} is too large: {myfile.size} bytes. "
                f"Maximum size is {MAX_UPLOAD_SIZE} bytes."
            )
            return render(request, "requestdataapp/file-upload.html", context=context, status=400)

        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        context["filename"] = filename

    return render(request, "requestdataapp/file-upload.html", context=context)
