# check known phrases
import json

# local data for testing purposes (incomplete)
test_data = ['prize', 'prizes', 'action required', 'your account will be', 'final notice', 'warning', 'payment details', 'click', 'selected', 'winner', 'urgent', 'secure download']

def check_known_phrases():
    print("TESTING")
    with open('../email-example/response_1762358375899.json', 'r') as email:
        # load email content
        data = json.load(email);
        message = data['body']['text'].replace("\n", " ").lower()

        # count phrases
        phrase_flags = 0 
        for phrase in test_data:
            phrase_flags += message.count(phrase)
        
        # any phrase raises suspicion, 3 instances gives cause it is likely
        return 2 if phrase_flags > 3 else 1 if phrase_flags > 1 else 0
        
print(check_known_phrases())