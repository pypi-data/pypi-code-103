# -*- coding:utf-8 -*-

from osc_openapi_framework import analyzer, schema


WAY_MAPPING = {
    'in': 'Request',
    'out': 'Response',
}


class Builder(object):
    inner_schemas = dict()

    def build(self, api):
        (objects, duplicate_in_call, duplicate) = analyzer.analyze(api.calls)
        for x in (w for v in duplicate for w in objects[v]):
            x.flag_uniq_by_call = True
        for x in (w for v in duplicate_in_call for w in objects[v]):
            x.flag_uniq_by_way = True
        res = {
            'info': api.infos,
            'paths': self.build_paths(api.calls),
            'security': api.security,
            'servers': api.servers,
        }
        res.update(self.build_components())
        return res

    def build_paths(self, calls):
        return {
            '/{}'.format(k): {
                v.http_verb: self.build_operation(v),
                'description': v.description
            } for k, v in calls.items()
        }

    def build_root_schema(self, name, fields, required=None, **kwargs):
        root_schema = {'required': required} if required else {}
        root_schema.update({
            'type': 'object',
            'properties': self.build_schema(fields, **kwargs)
        })
        self.inner_schemas[name] = root_schema
        return self.make_ref(name)

    def build_schema(self, fields, **kwargs):
        return {
            k: self.build_inner_schema(v, **kwargs)
            for k, v in fields.items()
        }

    def build_inner_schema(self, field, **kwargs):
        return (
            self.build_array if isinstance(field, schema.ArrayField) else
            self.build_object if isinstance(field, schema.ObjectField) else
            self.build_field
        )(field, **kwargs)

    def build_object(self, field, **kwargs):
        name = (
            "{}_{}".format(
                field.name, field.id
            ) if field.flag_uniq_by_call or field.flag_uniq_by_way
            else field.name
        )
        if name not in self.inner_schemas:
            self.inner_schemas[name] = {
                'type': 'object',
                'properties': self.build_schema(field.properties),
                'description': field.description,
            }
        return self.make_ref(name)

    def build_array(self, field, **kwargs):
        return {
            'type': 'array',
            'items': self.build_inner_schema(field.item, **kwargs),
            'description': field.description
        }

    def build_field(self, field, **kwargs):
        res = {'type': field.type, 'description': field.description}
        if field.format:
            res['format'] = field.format
        if field.default:
            res['default'] = field.default
        return res


class BuilderV2(Builder):
    def build(self, *args):
        res = super().build(*args)
        res.update({'swagger': '2.0'})
        return res

    def build_operation(self, call):
        return {
            'consumes': ['application/json'],
            'produces': ['application/json'],
            'parameters': [{
                'name': 'body',
                'in': 'body',
                'schema': self.build_root_schema(
                    "{}Request".format(call.name),
                    call.input_fields,
                    required=call.required,
                    call_name=call.name,
                )
            }],
            'responses': {
                '200': {
                    'schema': self.build_root_schema(
                        "{}Response".format(call.name),
                        call.output_fields,
                        call_name=call.name,
                    ),
                    'description': call.description_response
                }
            }
        }

    def make_ref(self, name):
        return {'$ref': '#/definitions/{}'.format(name)}

    def build_components(self):
        return {
            'definitions': self.inner_schemas
        }


class BuilderV3(Builder):
    def build(self, *args):
        res = super().build(*args)
        res.update({'openapi': '3.0.0'})
        return res

    def build_operation(self, call):
        call_name = call.name
        if '/' in call.name:
            call_name = call.name.replace('/', '_')
        return {
            'requestBody': {
                'content': {
                    'application/json': {
                        'schema': self.build_root_schema(
                            "{}Request".format(call_name),
                            call.input_fields,
                            required=call.required,
                            call_name=call.name,
                        )
                    }
                }
            },
            'responses': {
                '200': {
                   'content': {
                        'application/json': {
                            'schema': self.build_root_schema(
                                "{}Response".format(call_name),
                                call.output_fields,
                                call_name=call.name,
                            )
                        }
                    }, 'description': call.description_response
                }
            },
            'tags': [call.tag]
        }

    def make_ref(self, name):
        return {'$ref': '#/components/schemas/{}'.format(name)}

    def build_components(self):
        return {
            'components': {
                'schemas': self.inner_schemas
            }
        }
