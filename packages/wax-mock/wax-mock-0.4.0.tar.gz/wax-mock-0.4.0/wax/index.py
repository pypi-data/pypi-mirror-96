from wax.lessweb import Application, Context
from wax.lessweb.plugin.redisplugin import RedisPlugin
from wax.load_config import config


def allow_cors(ctx: Context):
    ctx.response.send_access_allow()
    return ctx()


app = Application()
app.add_plugin(RedisPlugin(**config['redis']))

app.add_interceptor('.*', method='*', dealer=allow_cors)
app.add_options_mapping('.*', lambda:'')

from wax.mock_api import mock_dealer, pql_playground, default_json, check_entities
from wax.tag_api import make_kotlin_code, make_solution_list, make_openapi_json
wax_api_prefix = config['mockapi-prefix']
app.add_mapping(f'{wax_api_prefix}/.*', method='*', dealer=mock_dealer)
app.add_get_mapping('/openapi.json', dealer=make_openapi_json)
app.add_get_mapping('/openapi.kt', dealer=make_kotlin_code)
app.add_get_mapping('/solution.md', dealer=make_solution_list)

from wax.tag_api import operation_list, operation_example, operation_detail, operation_edit_state, compare_swagger
app.add_get_mapping('/', operation_list)
app.add_get_mapping('/tag/{tag}', operation_list)
app.add_post_mapping('/op/state', operation_edit_state)
app.add_post_mapping('/op/diff', compare_swagger)
app.add_get_mapping('/op/{opId}', operation_detail)
app.add_get_mapping('/op/{opId}/example', operation_example)
app.add_post_mapping('/op/pql', pql_playground)
app.add_post_mapping('/op/mockjs/default', default_json)
app.add_post_mapping('/op/mockjs/check', check_entities)
