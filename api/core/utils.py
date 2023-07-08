def handle_response(response):
    if response.status_code == 200:
        try:
            return True, response.json()
        except ValueError:
            return True, response.text

    try:
        error_msg = response.json().get("message", "No detailed message provided.")
    except ValueError:
        error_msg = "No detailed message provided."

    error = {
        "message": "An error occurred during the request.",
        "status_code": response.status_code,
        "url": response.url,
        "details": error_msg,
    }

    return False, error
