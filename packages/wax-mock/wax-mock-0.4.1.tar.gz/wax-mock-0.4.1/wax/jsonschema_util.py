from typing import Dict, List, Tuple
import datetime
import json
from wax.lessweb.webapi import BadParamError


def deep_copy(obj):
    return json.loads(json.dumps(obj))


def make_row(level, name, types, description, additional, ref=''):
    return {'level': level, 'name': name, 'types': types, 'description': description, 'additional': additional, 'ref': ref}


def jsonschema_from_ref(ref: str, swagger_data: Dict) -> Dict:
    ret = swagger_data
    if '#' in ref:
        ref = ref.rsplit('#', 1)[-1]
    for seg in ref.split('/'):
        if not seg: continue
        ret = ret.get(seg, {})
    return ret


def jsonschema_to_rows(parent_level: str, name: str, schema: Dict, swagger_data: Dict, *, required: List) -> List:
    level = f'{parent_level}{name}/'
    additional = deep_copy(schema)
    for key in ['description', '$ref', 'type', 'items', 'properties']:
        additional.pop(key, '')
    description = schema.get('description', '')
    if '$ref' in schema:
        if level.count('/') > 40:  # 疑似循环引用
            return [make_row(level, name, schema['$ref'].split('/')[-1], description, additional)]
        ref_schema = jsonschema_from_ref(schema['$ref'], swagger_data)
        ret = jsonschema_to_rows(parent_level, name, ref_schema, swagger_data, required=[])
        if description:
            ret[0]['description'] = description
        if additional:
            ret[0]['additional'] = additional
        return ret
    types = schema.get('type', [])
    if not isinstance(types, list):
        types = [types]
    if name in required:
        types.append('!')
    if 'array' in types:
        items = schema.get('items', {})
        ret = [make_row(level, name, types, description, additional)]
        if items:
            ret.extend(jsonschema_to_rows(level, '[ ]', items, swagger_data, required=[]))
        return ret
    elif 'object' in types:
        properties = schema.get('properties', {})
        ret = [make_row(level, name, types, description, additional)]
        for key, val in properties.items():
            ret.extend(jsonschema_to_rows(level, key, val, swagger_data, required=additional.get('required', [])))
        return ret
    else:
        return [make_row(level, name, types, description, additional)]


def compare_json(level, actual, expect, full_actual, full_expect) -> List[str]:
    def item_to_pair(item) -> Tuple:
        if isinstance(item, str):
            return item, item
        if 'name' in item and 'in' in item:
            return item['name'], item
        if 'level' in item and 'types' in item:
            return item['level'], item
        if 'rows' in item and 'content_type' in item:
            return item.get('status_code', '') + ':' + item['content_type'], item['rows']
        raise NotImplementedError(item)

    if level.endswith((':examples', ':x-examples', ':items:description')):
        return []
    if level.count(':') > 50:  # 层级过深不再"深究"
        return []
    if type(actual) != type(expect):
        if actual or expect:
            return [f'{level} 定义不匹配 actual:{repr(actual)} expect:{repr(expect)}']
        else:
            return []
    if isinstance(actual, dict):
        ret = []
        if '$ref' in actual:
            actual = jsonschema_from_ref(actual['$ref'], full_actual)
        if '$ref' in expect:
            expect = jsonschema_from_ref(expect['$ref'], full_expect)

        actual_keys = actual.keys() - {'format'} if (actual.get('type') == 'integer' and actual.get('format') == 'int32') \
                    or (actual.get('type') == 'number' and actual.get('format') == 'double') else actual.keys()
        expect_keys = expect.keys() - {'format'} if (expect.get('type') == 'integer' and expect.get('format') == 'int32') \
                    or (actual.get('type') == 'number' and actual.get('format') == 'double') else expect.keys()
        if 'description' not in actual_keys or 'title' not in actual_keys:
            expect_keys -= {'description', 'title'}

        for key in actual_keys | expect_keys:
            ret.extend(compare_json(f'{level}:{key}', actual.get(key), expect.get(key), full_actual, full_expect))
        return ret
    elif isinstance(actual, list):
        actual_dict = dict(item_to_pair(item) for item in actual)
        expect_dict = dict(item_to_pair(item) for item in expect)
        return compare_json(level, actual_dict, expect_dict, full_actual, full_expect)
    elif actual != expect:
        return [f'{level} 不一致 actual:{repr(actual)} expect:{repr(expect)}']
    else:
        return []


def jsonschema_to_json(name: str, schema: Dict, swagger_data: Dict):
    if '$ref' in schema:
        ref_schema = jsonschema_from_ref(schema['$ref'], swagger_data)
        return jsonschema_to_json(name, ref_schema, swagger_data)
    types = schema.get('type', [])
    format = schema.get('format', '')
    if not isinstance(types, list):
        types = [types]
    if 'array' in types:
        items = schema.get('items', {})
        return [jsonschema_to_json(name, items, swagger_data)]
    elif 'object' in types:
        properties = schema.get('properties', {})
        return {key: jsonschema_to_json(key, val, swagger_data) for key, val in properties.items()}
    elif 'integer' in types:
        return 1
    elif 'number' in types:
        return 1.23
    elif 'boolean' in types:
        return True
    elif format == 'date-time':
        return datetime.datetime.now().isoformat() + 'Z'
    elif format == 'date':
        return datetime.date.today().isoformat()
    elif format == 'time':
        return datetime.datetime.now().time().isoformat().split('.')[0]
    else:
        return name.upper()
