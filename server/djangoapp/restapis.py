import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from functools import lru_cache

import os

API_KEY = os.environ.get('API_KEY')
API_ENDPOINT = os.environ.get('API_ENDPOINT')
GET_DEALERSHIP_ENDPOINT = f"{API_ENDPOINT}/get-dealership.json"
GET_REVIEWS_ENDPOINT = f"{API_ENDPOINT}/get-review.json"

NLU_ENDPOINT = os.environ.get('NLU_ENDPOINT')
NLU_API_KEY = os.environ.get('NLU_API_KEY')

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
        response = requests.post(url, headers={'Content-Type': 'application/json'},
                                 params=kwargs, json=json_payload)
        return response
    except Exception as e:
        # If any error occurs
        print("Exception", e)
    


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
        review=row["review"], 
        sentiment=analyze_review_sentiments(row["review"]),
        purchase=row["purchase"],
        purchase_date=row.get("purchase_date", None),
        make=row.get("car_make", None), 
        model=row.get("car_model", None), 
        year=row.get("car_year", None))

def get_dealers_from_cf():
    return get_from_cf(GET_DEALERSHIP_ENDPOINT, constructor_car_dealer)
def get_dealers_by_state(state):
    return get_from_cf(GET_DEALERSHIP_ENDPOINT, constructor_car_dealer, STATE=state)

# dealer id wont change so we can cache it
@lru_cache
def get_dealer_by_id(id):
    return get_from_cf(GET_DEALERSHIP_ENDPOINT, constructor_car_dealer, ID=id)

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_by_id(dealer_id):
    return get_from_cf(GET_REVIEWS_ENDPOINT, constructor_dealer_review, dealerId=dealer_id)

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(review_text):
    print(f"Analyzing text: {review_text}")

    endpoint = f"{NLU_ENDPOINT}/v1/analyze?version=2019-07-12"
    payload = {
        "text": review_text,
        "features": {
            "sentiment": {}
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    auth = ("apikey", NLU_API_KEY)

    response = requests.post(url=endpoint, json=payload, headers=headers, auth=auth)

    print(f"Response: {response.text}")

    return response.json()["sentiment"]["document"]["label"]

    

