from aiohttp import web
import os
import json
import uuid
from datetime import datetime as dt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def call_test(request):
    content = "get ok"
    return web.Response(text=content, content_type="text/html")


async def call_request(request):
    request_str = json.loads(str(await request.text()))
    prompts = json.loads(request_str)
    logger.info("call_request prompts: {}".format(prompts))
    for p in prompts:
        id = str(uuid.uuid4())
        filename = ''
        filename += 'd[' + str(dt.now().strftime('%Y-%m-%d-%H-%M-%S-%f')) + ']d-'
        filename += 'i[' + id + ']i-'
        filename += 'p[' + str(p['predictions_count']) + ']p-'
        filename += 'r[' + str(p['upscale_ratio']) + ']r'
        p['filename'] = filename
        with open('data/requests/'+filename, 'w') as f:
            f.write(p['prompt'])    
    
    return web.Response(text=json.dumps(prompts), content_type="text/html")


async def call_result(request):
    request_str = json.loads(str(await request.text()))
    filename = json.loads(request_str)
    logger.info("call_result filename: {}".format(filename))    
    return web.Response(text=filename, content_type="text/html")


def main():    
    logger.info("Starting server")
    app = web.Application(client_max_size=1024**3)
    app.router.add_route('GET', '/test', call_test)
    app.router.add_route('POST', '/request', call_request)
    app.router.add_route('POST', '/result', call_result)
    web.run_app(app, port=os.environ.get('PORT', ''))


if __name__ == "__main__":
    main()    
