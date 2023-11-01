

async def jlite_post(model_slug, action, data, api_token):
    import json
    import js
    from pyodide.ffi import to_js
    from js import Object

    action = action.strip().lower()
    model_slug = model_slug.strip()
    api_token = api_token.strip()
    assert isinstance(data, dict)
    data_str = json.dumps(data)

    resp = await js.fetch(f'https://biolm.ai/api/v1/models/{model_slug}/{action}/', to_js({
        "method": "POST",
        "body": data_str,
        "credentials": "same-origin",
        "headers": {"Content-Type": "application/json",
                    "Authorization": f"Token {api_token}"}
    }, dict_converter=Object.fromEntries))

    res = await resp.text()
    json_resp = json.loads(res)
    return json_resp