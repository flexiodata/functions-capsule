
# ---
# name: capsule-opportunities
# deployed: true
# config: index
# title: Capsule Opportunities
# description: Returns a list of opportunties from Capsule
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
#     description: The id of the opportunity
#   - name: name
#     type: string
#     description: The name of this opportunity
#   - name: description
#     type: string
#     description: A description of the opportunity
#   - name: value_amount
#     type: number
#     description: The amount the opportunity is worth
#   - name: value_currency
#     type: string
#     description: The currency type of the opportunity
#   - name: probability
#     type: integer
#     description: The probability of winning the opportunity
#   - name: created_at
#     type: string
#     description: The date the opportunity was created
#   - name: updated_at
#     type: string
#     description: The date when the opportunity was last updated
#   - name: expected_close_on
#     type: string
#     description: The expected close date of this opportunity
#   - name: closed_on
#     type: string
#     description: The date this opportunity was closed
#   - name: last_contacted_at
#     type: string
#     description: The date when this opportuntiy was last time contacted
#   - name: last_stage_changed_at
#     type: string
#     description: The date when this opportuntiy last had its milestone changes
#   - name: duration
#     type: integer
#     description: The duration of the opportunity
#   - name: duration_basis
#     type: string
#     description: The time unit for the duration
#   - name: milestone_id
#     type: integer
#     description: The id of the milestone for the opportunity
#   - name: milestone_name
#     type: string
#     description: The name of the milestone for the opportunity
#   - name: milestone_last_open_id
#     type: integer
#     description: The id of the last milestone selected on the opportuntiy while open
#   - name: milestone_last_open_name
#     type: string
#     description: The id of the last milestone selected on the opportuntiy while open
#   - name: lost_reason
#     type: string
#     description: The reason the opportunity was lost
#   - name: party_id
#     type: integer
#     description: The id of the party for the opportunity
#   - name: party_type
#     type: string
#     description: The type of party for the opportunity; either 'person' or 'organisation'
#   - name: party_name
#     type: string
#     description: The name of the party for the opportunity
#   - name: owner_id
#     type: integer
#     description: The id of the owner of the opportunity
#   - name: owner_name
#     type: string
#     description: The name of the owner of the opportunity
#   - name: team_id
#     type: integer
#     description: The id of the team associated with the person
#   - name: team_name
#     type: string
#     description: The name of the team associated with the person
# examples:
#   - '""'
#   - '"id, name, value_amount"'
# notes: |
#   See here for more information about Capsule opportunity properties: https://developer.capsulecrm.com/v2/models/opportunity
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
    for data in get_data(flex.vars):
        flex.output.write(data)

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
    url = 'https://api.capsulecrm.com/api/v2/opportunities'

    page_size = 100
    url_query_params = {'perPage': page_size}
    url_query_str = urllib.parse.urlencode(url_query_params)
    page_url = url + '?' + url_query_str

    while True:

        response = requests_retry_session().get(page_url, headers=headers)
        response.raise_for_status()
        content = response.json()
        data = content.get('opportunities',[])

        if len(data) == 0: # sanity check in case there's an issue with cursor
            break

        buffer = ''
        for item in data:
            item = get_item_info(item)
            buffer = buffer + json.dumps(item, default=to_string) + "\n"
        yield buffer

        page_url = (response.links.get('next') or {}).get('url')
        if page_url is None:
            break

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(429, 500, 502, 503, 504),
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

def get_item_info(item):

    # map this function's property names to the API's property names
    info = OrderedDict()

    info['id'] = item.get('id')
    info['name'] = item.get('name')
    info['description'] = item.get('description')
    info['value_amount'] = (item.get('value') or {}).get('amount')
    info['value_currency'] = (item.get('value') or {}).get('currency')
    info['probability'] = item.get('probability')
    info['created_at'] = to_date(item.get('createdAt'))
    info['updated_at'] = to_date(item.get('updatedAt'))
    info['expected_close_on'] = to_date(item.get('expectedCloseOn'))
    info['closed_on'] = to_date(item.get('closedOn'))
    info['last_contacted_at'] = to_date(item.get('lastContactedAt'))
    info['last_stage_changed_at'] = to_date(item.get('lastStageChangedAt'))
    info['duration'] = item.get('duration')
    info['duration_basis'] = item.get('durationBasis')
    info['milestone_id'] = (item.get('milestone') or {}).get('id')
    info['milestone_name'] = (item.get('milestone') or {}).get('name')
    info['milestone_last_open_id'] = (item.get('lastOpenMilestone') or {}).get('id')
    info['milestone_last_open_name'] = (item.get('lastOpenMilestone') or {}).get('name')
    info['lost_reason'] = item.get('lostReason')
    info['party_id'] = (item.get('owner') or {}).get('id')
    info['party_type'] = (item.get('owner') or {}).get('type')
    info['party_name'] = (item.get('owner') or {}).get('name')
    info['owner_id'] = (item.get('owner') or {}).get('id')
    info['owner_name'] = (item.get('owner') or {}).get('name')
    info['team_id'] = (item.get('team') or {}).get('id')
    info['team_name'] = (item.get('team') or {}).get('name')

    return info
