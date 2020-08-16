NODE_VALIDATION_SCHEMA = {
    'SampleNode': {
        'test_input': {},
        'expected_output': {
            'schema': str,
        }
    },
    'SchemaSampleModel': {
        'test_input': {
            'inputs': [1, 2, 3]
        },
        'expected_output': {
            'schema': {
                'type': dict,
                'fields': {
                    'results': int,
                },
            }
        }
    }
}
