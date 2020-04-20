
# ---
# name: capsule-opportunities
# deployed: true
# title: Capsule Opportunities
# description: Returns a list of opportunties from Capsule
# params:
#   - name: properties
#     type: array
#     description: The properties to return (defaults to all properties). See "Returns" for a listing of the available properties.
#     required: false
# returns:
#   - name: id
#     type: string
#     description: The id of the opportunity
#   - name: name
#     type: string
#     description: The name of this opportunity
#   - name: description
#     type: string
#     description: A description of the opportunity
#   - name: value_amt
#     type: string
#     description: The amount the opportunity is worth
#   - name: value_currency
#     type: string
#     description: The currency type of the opportunity
#   - name: probability
#     type: string
#     description: The probability of winning the opportunity
#   - name: created
#     type: string
#     description: The date the opportunity was created
#   - name: updated
#     type: string
#     description: The date when the opportunity was last updated
#   - name: expected_close
#     type: string
#     description: The expected close date of this opportunity
#   - name: closed
#     type: string
#     description: The date this opportunity was closed
#   - name: last_contacted
#     type: string
#     description: The date when this opportuntiy was last time contacted
#   - name: last_stage_changed
#     type: string
#     description: The date when this opportuntiy last had its milestone changes
#   - name: owner_id
#     type: string
#     description: The id of the owner of the opportunity
#   - name: owner_username
#     type: string
#     description: The username of the owner of the opportunity
#   - name: owner_name
#     type: string
#     description: The name of the owner of the opportunity
#   - name: owner_pictureurl
#     type: string
#     description: The url for the picture profile for the owner of the opportunity
#   - name: team
#     type: string
#     description: The team this opportunity is assigned to
#   - name: party_id
#     type: string
#     description: The id of the party for the opportunity
#   - name: party_type
#     type: string
#     description: The type of party for the opportunity; either 'person' or 'organisation'
#   - name: party_firstname
#     type: string
#     description: The first name of the party for the opportunity
#   - name: party_lastname
#     type: string
#     description: The last name of the party for the opportunity
#   - name: party_pictureurl
#     type: string
#     description: The url for the picture profile for the party for the opportunity
#   - name: duration
#     type: string
#     description: The duration of the opportunity
#   - name: duration_basis
#     type: string
#     description: The time unit for the duration
#   - name: milestone_id
#     type: string
#     description: The id of the milestone for the opportunity
#   - name: milestone_name
#     type: string
#     description: The name of the milestone for the opportunity
#   - name: milestone_last_open_id
#     type: string
#     description: The id of the last milestone selected on the opportuntiy while open
#   - name: milestone_last_open_name
#     type: string
#     description: The id of the last milestone selected on the opportuntiy while open
#   - name: lost_reason
#     type: string
#     description: The reason the opportunity was lost
# examples:
#   - '"*"'
#   - '"id, description, duration, duration_basis, value_amt, value_currency, probability"'
# notes: |
#   See here for more information about Capsule opportunity properties: https://developer.capsulecrm.com/v2/models/opportunity
# ---

import json
import requests
import urllib
import itertools
from datetime import *
from decimal import *
from cerberus import Validator
from collections import OrderedDict

# main function entry point
def flexio_handler(flex):

    # get the api key from the variable input
    auth_token = dict(flex.vars).get('capsule_connection',{}).get('access_token')
    if auth_token is None:
        flex.output.content_type = "application/json"
        flex.output.write([[""]])
        return

    # get the input
    input = flex.input.read()
    try:
        input = json.loads(input)
        if not isinstance(input, list): raise ValueError
    except ValueError:
        raise ValueError

    # define the expected parameters and map the values to the parameter names
    # based on the positions of the keys/values
    params = OrderedDict()
    params['properties'] = {'required': False, 'validator': validator_list, 'coerce': to_list, 'default': '*'}
    input = dict(zip(params.keys(), input))

    # validate the mapped input against the validator
    # if the input is valid return an error
    v = Validator(params, allow_unknown = True)
    input = v.validated(input)
    if input is None:
        raise ValueError

    # map this function's property names to the API's property names
    property_map = OrderedDict()
    property_map['id'] = lambda item: item.get('id','')
    property_map['name'] = lambda item: item.get('name','')
    property_map['description'] = lambda item: item.get('description','')
    property_map['value_amt'] = lambda item: item.get('value',{}).get('amount','')
    property_map['value_currency'] = lambda item: item.get('value',{}).get('currency','')
    property_map['probability'] = lambda item: item.get('probability','')
    property_map['created'] = lambda item: item.get('createdAt','')
    property_map['updated'] = lambda item: item.get('updatedAt','')
    property_map['expected_close'] = lambda item: item.get('expectedCloseOn','')
    property_map['closed'] = lambda item: item.get('closedOn','')
    property_map['last_contacted'] = lambda item: item.get('lastContactedAt','')
    property_map['last_stage_changed'] = lambda item: item.get('lastStageChangedAt','')
    property_map['owner_id'] = lambda item: item.get('owner',{}).get('id','')
    property_map['owner_username'] = lambda item: item.get('owner',{}).get('username','')
    property_map['owner_name'] = lambda item: item.get('owner',{}).get('name','')
    property_map['owner_pictureurl'] = lambda item: item.get('owner',{}).get('pictureURL','')
    property_map['team'] = lambda item: item.get('team','')
    property_map['party_id'] = lambda item: item.get('party',{}).get('id','')
    property_map['party_type'] = lambda item: item.get('party',{}).get('type','')
    property_map['party_firstname'] = lambda item: item.get('party',{}).get('firstName','')
    property_map['party_lastname'] = lambda item: item.get('party',{}).get('lastName','')
    property_map['party_pictureurl'] = lambda item: item.get('party',{}).get('pictureURL','')
    property_map['duration'] = lambda item: item.get('duration','')
    property_map['duration_basis'] = lambda item: item.get('durationBasis','')
    property_map['milestone_id'] = lambda item: item.get('milestone',{}).get('id','')
    property_map['milestone_name'] = lambda item: item.get('milestone',{}).get('name','')
    property_map['milestone_last_open_id'] = lambda item: item.get('lastOpenMilestone',{}).get('id','')
    property_map['milestone_last_open_name'] = lambda item: item.get('lastOpenMilestone',{}).get('name','')
    property_map['lost_reason'] = lambda item: item.get('lostReason','')

    try:

        # make the request
        # see here for more info: https://developer.capsulecrm.com/v2/operations/Opportunity

        url = 'https://api.capsulecrm.com/api/v2/opportunities'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + auth_token
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content = response.json()

        # get the properties to return and the property map
        properties = [p.lower().strip() for p in input['properties']]

        # if we have a wildcard, get all the properties
        if len(properties) == 1 and properties[0] == '*':
            properties = list(property_map.keys())

        # build up the result
        result = []
        result.append(properties)

        opportunities = content.get('opportunities',[])
        for item in opportunities:
            row = [property_map.get(p, lambda item: '')(item) or '' for p in properties]
            result.append(row)

        flex.output.content_type = "application/json"
        flex.output.write(result)

    except:
        flex.output.content_type = 'application/json'
        flex.output.write([['']])

def validator_list(field, value, error):
    if isinstance(value, str):
        return
    if isinstance(value, list):
        for item in value:
            if not isinstance(item, str):
                error(field, 'Must be a list with only string values')
        return
    error(field, 'Must be a string or a list of strings')

def to_string(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (Decimal)):
        return str(value)
    return value

def to_list(value):
    # if we have a list of strings, create a list from them; if we have
    # a list of lists, flatten it into a single list of strings
    if isinstance(value, str):
        return value.split(",")
    if isinstance(value, list):
        return list(itertools.chain.from_iterable(value))
    return None
