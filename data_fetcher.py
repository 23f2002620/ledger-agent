import json
import urllib.request
from typing import Dict, List, Any

def _fetch_url(url: str) -> Dict[str, Any]:
    """Fetch a URL and return JSON data with a common User-Agent."""
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def fetch_rates() -> Dict[str, float]:
    """Fetch currency conversion rates from the API.

    Returns:
        A dictionary mapping currency codes to USD per unit of that currency.
        Example: {'USD': 1.0, 'EUR': 1.04, 'INR': 0.01168}
    """
    url = ("https://exam.sanand.workers.dev/questionData?"
           "email=23f2002620%40ds.study.iitm.ac.in&quizSign=rEtcxqZXU6cz9ki2WpAapchXbXjkptKBXcKPWukFh2cJf%2Fp2fjULNcuGCK9N2g2klM0ly6Xso%2FbLonjaoSzLDW3LveOs71w%2B8jl3TU7%2BkLrI1SbyiQIBHK9V%2Be6wiw2P3ftZziijcQI45NbGnvE5gLWI7zoMdrKu998PsI4Hnu3WpsjwozOiUIK6%2BeWvYHjwIw4MKO1E8yrmFRyr%2BXXsIFxzOtr46rxA1Y3CYeKoXqO4LEfWJgxfBQNBqJmo23df8GW9TU5WKwoRMhWLPKrgUMnD8VESZ5eNSJ%2FBxCodq93L6KNJ3kOKN0BoWPN9qLwVVpZ3BsyPUVzjm9QqKE9UHQ%3D%3D&questionId=q-ledger-agent-server&path=%2Frates")
    return _fetch_url(url)['usd_per_unit']

def fetch_all_orders() -> List[Dict[str, Any]]:
    """Fetch all orders by paginating through the orders endpoint.

    Returns:
        A list of order dictionaries as provided by the API.
    """
    orders = []
    url = ("https://exam.sanand.workers.dev/questionData?"
           "email=23f2002620%40ds.study.iitm.ac.in&quizSign=rEtcxqZXU6cz9ki2WpAapchXbXjkptKBXcKPWukFh2cJf%2Fp2fjULNcuGCK9N2g2klM0ly6Xso%2FbLonjaoSzLDW3LveOs71w%2B8jl3TU7%2BkLrI1SbyiQIBHK9V%2Be6wiw2P3ftZziijcQI45NbGnvE5gLWI7zoMdrKu998PsI4Hnu3WpsjwozOiUIK6%2BeWvYHjwIw4MKO1E8yrmFRyr%2BXXsIFxzOtr46rxA1Y3CYeKoXqO4LEfWJgxfBQNBqJmo23df8GW9TU5WKwoRMhWLPKrgUMnD8VESZ5eNSJ%2FBxCodq93L6KNJ3kOKN0BoWPN9qLwVVpZ3BsyPUVzjm9QqKE9UHQ%3D%3D&questionId=q-ledger-agent-server&path=%2Forders&page=1")

    while url:
        data = _fetch_url(url)
        orders.extend(data['orders'])
        url = data.get('next')
    return orders