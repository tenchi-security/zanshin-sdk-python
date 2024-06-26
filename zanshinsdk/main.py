API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJlMGZjODJkMC01MDYxLTQ1ZmEtOWE0ZS00YjE5OGQzMjdlYWQiLCJpYXQiOjE3MTY4MzE0Njl9.OBriSHyimRLad-lYbTMAaHKcT0HFAJ4GyZrhBTuFn3Y"
API_URL = "https://api.zanshin.tenchi-dev.com"
ACME_BLUE = "00000000-ffff-4000-a000-000000000001"
ACME_RED = "6bf9bdf5-7da3-4696-8cb5-c300dcb8732b"
LAST_CURSOR = ""

import zanshinsdk
import pprint

pp = pprint.PrettyPrinter(indent=2)

def main():
  sdk = zanshinsdk.Client(api_key=API_KEY, api_url=API_URL)

  organization_id = ACME_RED

  followings = list(sdk.iter_organization_following(organization_id))

  following_ids = [
    f["id"] for f in followings if f["id"] == ACME_BLUE
  ]

  alerts_histories = sdk.iter_alerts_following_history(
      organization_id, 
      following_ids,
      page_size=1000,
      cursor=LAST_CURSOR
  )

  for alert_history in alerts_histories:
    pp.pprint(alert_history)


if __name__ == '__main__':
  main()