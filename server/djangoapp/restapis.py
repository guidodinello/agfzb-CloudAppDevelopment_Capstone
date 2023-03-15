import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

from .config_reader import ConfigReader
CONFIG = ConfigReader.getInstance().read_config()

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(f"GET from {url} with params {kwargs}")
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, 
                                headers={'Content-Type': 'application/json'},
                                params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    print(f"With status {response.status_code}")
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(f"POST to {url} with params {kwargs}")
    try:
        # Call get method of requests library with URL and parameters
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")

    print(f"With status {response.status_code}")
    return response


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

# Strategy Pattern - Strategy
def get_from_cf(url, constructor, **kwargs):
    json_result = get_request(url, **kwargs)
    print(json_result)
    if json_result['statusCode'] != 200:
        return []
    return [constructor(row) for row in json_result["body"]]

# Concrete Strategy 1
def constructor_car_dealer(row):
    return CarDealer(
        address=row["address"], 
        city=row["city"], 
        full_name=row["full_name"],
        id=row["id"], 
        lat=row["lat"], 
        long=row["long"],
        short_name=row["short_name"],
        st=row["st"], 
        zip=row["zip"],
        state=row["state"])

# Concrete Strategy 2
def constructor_dealer_review(row):
    return DealerReview(
        id=row["id"],
        dealership=row["dealership"], 
        name=row["name"], 
        purchase=row["purchase"],
        review=row["review"], 
        purchase_date=row["purchase_date"],
        make=row["car_make"], 
        model=row["car_model"], 
        year=row["car_year"],
        sentiment=analyze_review_sentiments(row["review"]))

def get_dealers_from_cf():
    url = f"{CONFIG['API_ENDPOINT']}{CONFIG['GET_DEALERSHIP']}"
    return get_from_cf(url, constructor_car_dealer)
def get_dealers_by_state(url, state):
    url = f"{CONFIG['API_ENDPOINT']}{CONFIG['GET_DEALERSHIP']}"
    return get_from_cf(url, constructor_car_dealer, STATE=state)

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_by_id(dealer_id):
    url = f"{CONFIG['API_ENDPOINT']}{CONFIG['GET_REVIEW']}"
    return get_from_cf(url, constructor_dealer_review, dealerId=dealer_id)

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(review_text):
    print(f"Analyzing text: {review_text}")
    params = {
        'version': '2021-09-01',
        'features': {
            'entities': {},
            'keywords': {}
        }
    }

    data = { 'text': review_text }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Basic {CONFIG['NLU_API_KEY']}"
    }

    response = requests.post(CONFIG['NLU_URL'], headers=headers, params=params, json=data)

    

