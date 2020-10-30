## Tune Server Helper

REST API to trigger Ray Tune

`GET /api/models`
List available models

`POST /api/tune/start`
Start a tune

`GET /api/tune?model_class=xxx`
Get all tune experiments for a model class

`GET /api/tune/{id}?model_class=xxx`
Query specific details about an experiment. This returns all the trails and metrics.
