async def jlite_post(model_slug, action, data, api_token):
    import json

    import js
    from pyodide.ffi import to_js

    action = action.strip().lower()
    model_slug = model_slug.strip()
    api_token = api_token.strip()
    assert isinstance(data, dict)
    data_str = json.dumps(data)

    resp = await js.fetch(
        f"https://biolm.ai/api/v1/models/{model_slug}/{action}/",
        to_js(
            {
                "method": "POST",
                "body": data_str,
                "credentials": "same-origin",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Token {api_token}",
                },
            },
            dict_converter=js.Object.fromEntries,
        ),
    )

    res = await resp.text()
    json_resp = json.loads(res)
    return json_resp


async def requests_post(model_slug, action, data, api_token):
    import json

    import requests

    action = action.strip().lower()
    model_slug = model_slug.strip()
    api_token = api_token.strip()
    assert isinstance(data, dict)
    data_str = json.dumps(data)

    resp = requests.post(
        f"https://biolm.ai/api/v1/models/{model_slug}/{action}/",
        data=data_str,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {api_token}",
        },
    )

    json_resp = resp.json()
    return json_resp


async def get_api_function():
    import importlib.util

    if importlib.util.find_spec("js"):
        return jlite_post
    else:
        return requests_post


async def api_caller(model_slug, action, data, api_token):
    params = {
        "model_slug": model_slug,
        "action": action,
        "data": data,
        "api_token": api_token,
    }
    import importlib.util

    if importlib.util.find_spec("js"):
        return await jlite_post(**params)
    else:
        return await requests_post(**params)
