import os
import json
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from inference import model_fn, input_fn, predict_fn, output_fn
import uvicorn

app = FastAPI()

model = model_fn('/opt/ml/model')

@app.get('/ping')
def ping():
    health = model is not None
    status_code = 200 if health else 404
    return Response(content='\n', status_code=status_code, media_type='application/json')

@app.post('/invocations')
async def invocations(request: Request):
    content_type = request.headers.get('Content-Type', '')
    data = await request.body()
    data = data.decode('utf-8')

    input_data = input_fn(data, content_type)
    prediction = predict_fn(input_data, model)
    result = output_fn(prediction, content_type)

    return JSONResponse(content=json.loads(result))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
