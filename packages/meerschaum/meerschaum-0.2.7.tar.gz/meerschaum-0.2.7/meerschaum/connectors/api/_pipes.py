#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Register or fetch Pipes from the API
"""

from __future__ import annotations
from meerschaum.utils.typing import SuccessTuple, Union, Any, Optional, Mapping, List
from meerschaum.utils.debug import dprint
from meerschaum.utils.warnings import error

def pipe_r_url(
        pipe : 'meerschaum.Pipe'
    ) -> str:
    """
    Generate a relative URL path from a Pipe's keys.
    """
    from meerschaum.config.static import _static_config
    location_key = pipe.location_key
    if location_key is None: location_key = '[None]'
    return f"{_static_config()['api']['endpoints']['pipes']}/{pipe.connector_keys}/{pipe.metric_key}/{location_key}"

def register_pipe(
        self,
        pipe : meerschaum.Pipe,
        debug : bool = False
    ) -> SuccessTuple:
    """
    Submit a POST to the API to register a new Pipe object.
    Returns a tuple of (success_bool, response_dict)
    """
    from meerschaum.config.static import _static_config
    ### NOTE: if `parameters` is supplied in the Pipe constructor,
    ###       then `pipe.parameters` will exist and not be fetched from the database.
    response = self.post(_static_config()['api']['endpoints']['pipes'], json=pipe.meta, debug=debug)
    if debug: dprint(response.text)
    if isinstance(response.json(), list):
        response_tuple = response.__bool__(), response.json()[1]
    elif 'detail' in response.json():
        response_tuple = response.__bool__(), response.json()['detail']
    else:
        response_tuple = response.__bool__(), response.text
    return response_tuple

def edit_pipe(
        self,
        pipe : meerschaum.Pipe,
        patch : bool = False,
        debug : bool = False,
        **kw : Any
    ) -> SuccessTuple:
    """
    Submit a PATCH to the API to edit an existing Pipe.
    Returns a tuple of (success_bool, response_dict)
    """
    from meerschaum.config.static import _static_config
    if debug:
        from meerschaum.utils.debug import dprint
        dprint(f"patch: {patch}")
    response = self.patch(
        _static_config()['api']['endpoints']['pipes'],
        json = pipe.meta,
        params = {'patch' : patch},
        debug = debug
    )
    return response.__bool__(), response.json()

def fetch_pipes_keys(
        self,
        connector_keys : list = [],
        metric_keys : list = [],
        location_keys : list = [],
        params : dict = dict(),
        mrsm_instance : str = 'api',
        debug : bool = False
    ) -> Union[List[str], Mapping[str, Any]]:
    """
    NOTE: This function no longer builds Pipes. Use the main `get_pipes()` function
          with the arguments `mrsm_instance = 'api' and `method = 'registered'` (default).

    Fetch registered Pipes' keys from the API.

    keys_only : bool : True
        If True, only return a list of tuples of the keys
        E.g. [ (connector_keys, metric_key, location_key) ]
        This is used by the main `get_pipes()` function for the 'api' method.
    """
    from meerschaum.utils.debug import dprint
    from meerschaum.utils.warnings import error
    from meerschaum.config.static import _static_config
    import json

    r_url = _static_config()['api']['endpoints']['pipes'] + '/keys'
    try:
        j = self.get(
            r_url,
            params = {
                'connector_keys' : json.dumps(connector_keys),
                'metric_keys' : json.dumps(metric_keys),
                'location_keys' : json.dumps(location_keys),
                'params' : json.dumps(params),
                'debug' : debug,
            },
            debug=debug
        ).json()
    except Exception as e:
        error(str(e))

    if 'detail' in j: error(j['detail'], stack=False)
    result = []
    for t in j:
        result.append( (t['connector_keys'], t['metric_key'], t['location_key']) )
    return result

def sync_pipe(
        self,
        pipe : Optional[meerschaum.Pipe] = None,
        df : Optional[pandas.DataFrame] = None,
        debug : bool = False,
        **kw : Any
    ) -> SuccessTuple:
    """
    Append a pandas DataFrame to a Pipe.
    If Pipe does not exist, it is registered with supplied metadata
        NOTE: columns['datetime'] must be set for new Pipes.
    """
    from meerschaum.utils.debug import dprint
    from meerschaum.utils.warnings import warn
    from meerschaum.utils.misc import json_serialize_datetime
    import json
    if df is None:
        msg = f"DataFrame is None. Cannot sync pipe '{pipe}"
        return False, msg

    ### allow syncing dict or JSON without needing to import pandas (for IOT devices)
    if isinstance(df, dict):
        json_str = json.dumps(df, default=json_serialize_datetime)
    elif isinstance(df, str):
        json_str = df
    else:
        json_str = df.to_json(date_format='iso', date_unit='us')

    ### Send columns in case the user has defined them locally.
    if pipe.columns:
        kw['columns'] = json.dumps(pipe.columns)
    r_url = pipe_r_url(pipe) + '/data'
    if debug: dprint(f"Posting data to {r_url}...")
    try:
        response = self.post(
            r_url,
            ### handles check_existing
            params = kw,
            data = json_str,
            debug = debug
        )
    except Exception as e:
        warn(str(e))
        return False, str(e)
        
    j = response.json()
    if isinstance(j, dict) and 'detail' in j:
        return False, j['detail']

    return tuple(j)

def delete_pipe(
        self,
        pipe : Optional[meerscahum.Pipe] = None,
        debug : bool = None,        
    ) -> SuccessTuple:
    """
    Delete a Pipe and drop its table.
    """
    from meerschaum.utils.warnings import error
    if pipe is None: error(f"Pipe cannot be None.")
    return self.do_action(
        ['delete', 'pipes'],
        connector_keys = pipe.connector_keys,
        metric_keys = pipe.metric_key,
        location_keys = pipe.location_key,
        force = True,
        debug = debug
    )

def get_pipe_data(
        self,
        pipe : meerschaum.Pipe,
        begin : Optional[datetime.datetime] = None,
        end : Optional[datetime.datetime] = None,
        params : Optional[Dict[str, Any]] = None,
        debug : bool = False
    ) -> pandas.DataFrame:
    """
    Fetch data from the API
    """
    from meerschaum.utils.warnings import warn
    r_url = pipe_r_url(pipe)
    try:
        response = self.get(r_url + "/data", json=params, params={'begin': begin, 'end': end}, debug=debug)
    except Exception as e:
        warn(str(e))
        return None
    if not response:
        if 'detail' in response.json():
            return False, response.json()['detail']
    from meerschaum.utils.packages import import_pandas
    from meerschaum.utils.misc import parse_df_datetimes
    pd = import_pandas()
    try:
        df = pd.read_json(response.text)
    except Exception as e:
        warn(str(e))
        return None
    df = parse_df_datetimes(pd.read_json(response.text), debug=debug)
    #  if debug: dprint(df)
    return df

def get_backtrack_data(
        self,
        pipe : meerschaum.Pipe,
        begin : datetime.datetime,
        backtrack_minutes : int = 0,
        debug : bool = False
    ) -> pandas.DataFrame:
    """
    Get a Pipe's backtrack data from the API.
    """
    from meerschaum.utils.debug import dprint
    from meerschaum.utils.warnings import warn
    r_url = pipe_r_url(pipe)
    try:
        response = self.get(
            r_url + "/backtrack_data",
            params = {
                'begin': begin,
                'backtrack_minutes': backtrack_minutes,
            },
            debug = debug
        )
    except Exception as e:
        warn(f"Failed to parse backtrack data JSON for pipe '{pipe}'. Exception:\n" + str(e))
        return None
    from meerschaum.utils.packages import import_pandas
    from meerschaum.utils.misc import parse_df_datetimes
    if debug: dprint(response.text)
    pd = import_pandas()
    try:
        df = pd.read_json(response.text)
    except Exception as e:
        warn(str(e))
        return None
    df = parse_df_datetimes(pd.read_json(response.text), debug=debug)
    #  if debug: dprint(df)
    return df

def get_pipe_id(
        self,
        pipe : meerschuam.Pipe,
        debug : bool = False,
    ) -> int:
    """
    Get a Pipe's ID from the API
    """
    from meerschaum.utils.debug import dprint
    r_url = pipe_r_url(pipe)
    response = self.get(
        r_url + '/id',
        debug = debug
    )
    if debug: dprint(response.text)
    try:
        return int(response.text)
    except:
        return None

def get_pipe_attributes(
        self,
        pipe : meerschaum.Pipe,
        debug : bool = False,
    ) -> Mapping[str, Any]:
    """
    Get a Pipe's attributes from the API
    """
    r_url = pipe_r_url(pipe)
    response = self.get(r_url + '/attributes', debug=debug)
    import json
    try:
        return json.loads(response.text)
    except:
        return None

def get_sync_time(
        self,
        pipe : 'meerschaum.Pipe',
        params : dict = None,
        debug : bool = False,
    ) -> datetime.datetime:
    """
    Get a Pipe's most recent datetime value from the API
    """
    import datetime, json
    r_url = pipe_r_url(pipe)
    response = self.get(r_url + '/sync_time', json=params, params={'debug' : debug}, debug=debug)
    try:
        dt = datetime.datetime.fromisoformat(json.loads(response.text))
    except:
        df = None
    return dt

def pipe_exists(
        self,
        pipe : 'meerschaum.Pipe',
        debug : bool = False
    ) -> bool:
    """
    Consult the API to see if a Pipe exists
    """
    r_url = pipe_r_url(pipe)
    response = self.get(r_url + '/exists', debug=debug)
    if debug: dprint("Received response: " + str(response.text))
    j = response.json()
    if isinstance(j, dict) and 'detail' in j:
        return False, j['detail']
    return j

def create_metadata(
        self,
        debug : bool = False
    ) -> bool:
    """
    Create Pipe metadata tables
    """
    from meerschaum.config.static import _static_config
    import json
    r_url = _static_config()['api']['endpoints']['metadata']
    response = self.post(r_url, debug=debug)
    if debug: dprint("Create metadata response: {response.text}")
    return json.loads(response.text)

def get_pipe_rowcount(
        self,
        pipe : 'meerschaum.Pipe',
        begin : 'datetime.datetime' = None,
        end : 'datetime.datetime' = None,
        params : Optional[Dict[str, Any]] = None,
        remote : bool = False,
        debug : bool = False,
    ) -> Optional[int]:
    """
    Get a pipe's row couunt from the API.
    """
    import json
    r_url = pipe_r_url(pipe)
    response = self.get(
        r_url + "/rowcount",
        json = params,
        params = {
            'begin' : begin,
            'end' : end,
            'remote' : remote,
        }
    )
    try:
        return int(json.loads(response.text))
    except:
        return None

def drop_pipe(
        self,
        pipe : meerschaum.Pipe,
        debug : bool = False
    ) -> SuccessTuple:
    """
    Drop a pipe's tables but maintain its registration.
    """
    return self.do_action(
        ['drop', 'pipes'],
        connector_keys = pipe.connector_keys,
        metric_keys = pipe.metric_key,
        location_keys = pipe.location_key,
        force = True,
        debug = debug
    )

