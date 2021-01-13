from datetime import datetime
from NeuralNetwork import neuralNetwork
import aiohttp
from aiohttp import web
import cv2
import numpy as np
import math as m

from detector import detect_iris

routes = web.RouteTableDef()


def processing(pupil: float, lux: float) -> str:
    return str(neuralNetwork(lux, pupil))


@routes.post('/detect')
async def iris_detect(request: web.Request):
    lux = float(request.query["lux"])
    reader = aiohttp.MultipartReader.from_response(request)
    file = await reader.next()
    content = bytes(await file.read())
    img_arr = np.fromstring(content, np.uint8)
    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

    img, result = detect_iris(img)

    now = datetime.now().strftime("%d.%m %H.%M.%S")
    with open(f"./results/{now}.jpg", "wb") as f:
        f.write(cv2.imencode('.jpg', img)[1].tostring())

    if result:
        return web.Response(body=processing(result, lux))
    else:
        return web.Response(body="Зрачки не распознаны!")


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=80)
