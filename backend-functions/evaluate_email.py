import check_content
import check_email
import check_known_phrases

def evaluate_email(email):
    body = email.get("body", {})
    message = body.get("text", "")

    content_result = check_content.check_content(message)
    address_result = check_email.check_email(email)
    known_phrase_result = check_known_phrases.check_known_phrases(email)

    return {"content_result": content_result, "address_result": address_result, "known_phrase_result": known_phrase_result}