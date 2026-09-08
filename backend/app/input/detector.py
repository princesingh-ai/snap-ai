def has_image_input(messages: list[dict]) -> bool:
    for message in messages:
        content = message.get("content")

        if not isinstance(content, list):
            continue

        for item in content:
            if item.get("type") == "image_url":
                return True

    return False

def has_pdf_input(messages: list[dict]) -> bool:
    for message in messages:
        content = message.get("content")

        if not isinstance(content, list):
            continue

        for item in content:
            if item.get("type") != "text":
                continue

            text = item.get("text", "")

            if "--- PDF File:" in text:
                return True

    return False

def has_document_input(messages: list[dict]) -> bool:
    return has_image_input(messages) or has_pdf_input(messages)