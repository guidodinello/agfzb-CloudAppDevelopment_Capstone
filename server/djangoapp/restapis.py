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
        response = requests.get(url, headers={'Content-Type': 'application/json'},
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


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, **kwargs)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer["address"], 
                city=dealer["city"], 
                full_name=dealer["full_name"],
                id=dealer["id"], 
                lat=dealer["lat"], 
                long=dealer["long"],
                short_name=dealer["short_name"],
                st=dealer["st"], 
                zip=dealer["zip"],
                state=dealer["state"])
            results.append(dealer_obj)

    return results

def get_dealers_by_state(url, state):
    return get_dealers_from_cf(url, STATE=state)

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url, **kwargs)
    print(json_result)
    if json_result:
        reviews  = json_result["reviews"]
        for review in reviews:
            review_obj = DealerReview(
                dealership=review["dealership"], 
                name=review["name"], 
                purchase=review["purchase"],
                review=review["review"], 
                purchase_date=review["purchase_date"],
                car_make=review["car_make"], 
                car_model=review["car_model"], 
                car_year=review["car_year"],
                sentiment=analyze_review_sentiments(str(review_obj.review)))
            results.append(review_obj)
    return results

def get_dealer_reviews_by_id(url, dealer_id):
    return get_dealer_reviews_from_cf(url, dealerId=dealer_id)

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
        'Authorization': f"Basic {CONFIG.NLU_API_KEY}"
    }

    response = requests.post(CONFIG.NLU_URL, headers=headers, params=params, json=data)

