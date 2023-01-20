import json, os, requests


def get_api_token():
    """Get a BioLM API token to use with future API requests.
    
    Copied from https://api.biolm.ai/#d7f87dfd-321f-45ae-99b6-eb203519ddeb.
    """
    url = "https://biolm.ai/api/auth/token/"

    payload = json.dumps({
      "username": os.environ.get("BIOLM_USER"),
      "password": os.environ.get("BIOLM_PASS")
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    
    os.environ['BIOLM_ACCESS'] = response_json['access']
    os.environ['BIOLM_REFRESH'] = response_json['refresh']

    return response_json



def esm2_transform(seq):
    """Make a POST request to get the ESM2 transforms for a protein sequence."""
    url = "https://biolm.ai/api/v1/models/esm2_t33_650M_UR50D/transform/"
    
    # Normally would POST multiple sequences at once for greater efficiency,
    # but for simplicity sake will do one at at time right now
    payload = json.dumps({
      "instances": [
        {
          "data": {
            "text": seq
          }
        }
      ]
    })
    
    try:
        access = os.environ.get('BIOLM_ACCESS')
        assert access
        refresh = os.environ.get('BIOLM_REFRESH')
        assert refresh
    except AssertionError:
        raise AssertionError("BioLM access or refresh token not set")
    
    headers = {
      'Cookie': 'access={};refresh={}'.format(access, refresh),
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    resp_json = response.json()
    transformations = resp_json['predictions']  # List, containing dicts for each sequence POSTed
    
    return transformations  # list of dict_keys(['name', 'mean_representations', 'contacts', 'logits', 'attentions'])


def esmfold_pdb(seq):
    """Make a POST request to predict a PDB file using ESMFold (i.e. ESM2)."""
    url = "https://biolm.ai/api/v1/models/esmfold-singlechain/predict/"
    
    # Normally would POST multiple sequences at once for greater efficiency,
    # but for simplicity sake will do one at at time right now
    payload = json.dumps({
      "instances": [
        {
          "data": {
            "text": seq
          }
        }
      ]
    })
    
    try:
        access = os.environ.get('BIOLM_ACCESS')
        assert access
        refresh = os.environ.get('BIOLM_REFRESH')
        assert refresh
    except AssertionError:
        raise AssertionError("BioLM access or refresh token not set")
    
    headers = {
      'Cookie': 'access={};refresh={}'.format(access, refresh),
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    resp_json = response.json()  
    # resp_json['predictions']  # List, one item for each sequence POSTed
    
    return resp_json['predictions'][0]