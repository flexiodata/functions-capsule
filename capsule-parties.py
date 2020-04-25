
# ---
# name: capsule-parties
# deployed: true
# config: index
# title: Capsule Parties
# description: Returns a list of parties from Capsule
# params:
#   - name: properties
#     type: array
#     description: The properties to return (defaults to all properties). See "Returns" for a listing of the available properties.
#     required: false
#   - name: filter
#     type: string
#     description: Filter to apply with key/values specified as a URL query string where the keys correspond to the properties to filter.
#     required: false
# returns:
#   - name: id
#     type: integer
#     description: The unique id of the party
#   - name: type
#     type: string
#     description: Whether a party is a person or an organisation
#   - name: first_name
#     type: string
#     description: The first name of the person if the party is a person
#   - name: last_name
#     type: string
#     description: The last name of the person if the party is a person
#   - name: title
#     type: string
#     description: The title of the person if the party is a person
#   - name: job_title
#     type: string
#     description: The job title of the person if the party is a person
#   - name: organisation_id
#     type: integer
#     description: The id of the organisation associated with the party
#   - name: organisation_name
#     type: string
#     description: The name of the organisation associated with the party
#   - name: organisation_type
#     type: string
#     description: The type of the organisation associated with the party
#   - name: organisation_picture_url
#     type: string
#     description: A URL the represents the location of the profile picture for the organisation associated with the party
#   - name: name
#     type: string
#     description: The name of the organisation if the party type is an organisation
#   - name: about
#     type: string
#     description: A short description of the party
#   - name: created_at
#     type: string
#     description: The date/time when the party was created
#   - name: updated_at
#     type: string
#     description: The date/time when the party was last updated
#   - name: last_contacted_at
#     type: string
#     description: The date/time when the party was last contacted
#   - name: address_id
#     type: integer
#     description: The id of the address associated with the party
#   - name: address_type
#     type: string
#     description: The type of the address associated with the party
#   - name: address_street
#     type: string
#     description: The street of the address associated with the party
#   - name: address_city
#     type: string
#     description: The city of the address associated with the party
#   - name: address_state
#     type: string
#     description: The state of the address associated with the party
#   - name: address_country
#     type: string
#     description: The country of the address associated with the party
#   - name: address_zip
#     type: string
#     description: The zip of the address for the party
#   - name: picture_url
#     type: string
#     description: A URL the represents the location of the profile picture for the party
#   - name: owner_id
#     type: integer
#     description: The id of the owner for the party
#   - name: owner_username
#     type: integer
#     description: The username of the owner for the party
#   - name: owner_name
#     type: integer
#     description: The name of the owner for the party
#   - name: team_id
#     type: integer
#     description: The id of the team associated with the party
#   - name: team_name
#     type: string
#     description: The name of the team associated with the party
# examples:
#   - '""'
#   - '"id, type, first_name, last_name, name"'
# notes: |
#   See here for more information about Capsule party properties: https://developer.capsulecrm.com/v2/models/party
# ---

import json
import urllib
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import *
from decimal import *
from collections import OrderedDict

# main function entry point
def flexio_handler(flex):

    flex.output.content_type = 'application/x-ndjson'
    for item in get_data(flex.vars):
        result = json.dumps(item, default=to_string) + "\n"
        flex.output.write(result)

def get_data(params):

    # get the api key from the variable input
    auth_token = dict(params).get('capsule_connection',{}).get('access_token')

    # see here for more info:
    # https://developer.capsulecrm.com/v2/operations/Opportunity

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + auth_token
    }
    url = 'https://api.capsulecrm.com/api/v2/parties'

    page_size = 100
    url_query_params = {'perPage': page_size}
    url_query_str = urllib.parse.urlencode(url_query_params)
    page_url = url + '?' + url_query_str

    while True:

        response = requests_retry_session().get(page_url, headers=headers)
        response.raise_for_status()
        content = response.json()
        data = content.get('parties',[])

        if len(data) == 0: # sanity check in case there's an issue with cursor
            break

        for header_item in data:
            detail_items_all =  header_item.get('addresses',[])
            if len(detail_items_all) == 0:
                yield get_item_info(header_item, {}) # if we don't have any addresses, make sure to return item header info
            else:
                for detail_item in detail_items_all:
                    yield get_item_info(header_item, detail_item)

        page_url = response.links.get('next',{}).get('url')
        if page_url is None:
            break

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def to_date(value):
    # TODO: convert if needed
    return value

def to_string(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (Decimal)):
        return str(value)
    return value

def get_item_info(header_item, detail_item):

    # map this function's property names to the API's property names
    info = OrderedDict()

    info['id'] = header_item.get('id')
    info['type'] = header_item.get('type')
    info['first_name'] = header_item.get('firstName')
    info['last_name'] = header_item.get('lastName')
    info['title'] = header_item.get('title')
    info['job_title'] = header_item.get('jobTitle')
    info['organisation_id'] = (header_item.get('organisation') or {}).get('id')
    info['organisation_name'] = (header_item.get('organisation') or {}).get('name')
    info['organisation_type'] = (header_item.get('organisation') or {}).get('type')
    info['organisation_picture_url'] = (header_item.get('organisation') or {}).get('pictureURL')
    info['name'] = header_item.get('name')
    info['about'] = header_item.get('about')
    info['created_at'] = to_date(header_item.get('createdAt'))
    info['updated_at'] = to_date(header_item.get('updatedAt'))
    info['last_contacted_at'] = to_date(header_item.get('lastContactedAt'))
    info['address_id'] = detail_item.get('id')
    info['address_type'] = detail_item.get('type')
    info['address_street'] = detail_item.get('street')
    info['address_city'] = detail_item.get('city')
    info['address_state'] = detail_item.get('state')
    info['address_country'] = detail_item.get('country')
    info['address_zip'] = detail_item.get('zip')
    info['picture_url'] = header_item.get('pictureURL')
    info['owner_id'] = (header_item.get('owner') or {}).get('id')
    info['owner_username'] = (header_item.get('owner') or {}).get('username')
    info['owner_name'] = (header_item.get('owner') or {}).get('name')
    info['team_id'] = (header_item.get('team') or {}).get('id')
    info['team_name'] = (header_item.get('team') or {}).get('name')

    # TODO:
    # add phone/email contact info

    return info
