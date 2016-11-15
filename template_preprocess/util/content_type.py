HTML_TYPES = ["html"]


def filename_is_html(filename):
    for ext in HTML_TYPES:
        if filename.endswith(ext):
            return True
    return False
