from aiohttp import web
import aiohttp_cors

import os
import json
import uuid
from datetime import datetime as dt
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*")
})


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
    requested_file_name = json.loads(request_str)
    logger.info("call_result filename: {}".format(requested_file_name))
    upscaled_path = './data/upscaled/'
    files = os.listdir(upscaled_path)
    # check if file with name filename* in 'data/generated' folder
    for file_name in sorted(files):
        if file_name.startswith(requested_file_name):
            # return file
            with open(upscaled_path+file_name, "rb") as f:
                data = f.read()
            # remove file from 'data/upscaled' folder if exists
            if os.path.exists(upscaled_path+file_name):
                os.remove(upscaled_path+file_name)
            return web.Response(body=data, content_type="image/png")
    return web.Response(text="File not found", content_type="text/html")


def main():    
    logger.info("Starting server")
    app = web.Application(client_max_size=1024**3)
    app.router.add_route('GET', '/test', call_test)
    app.router.add_route('POST', '/request', call_request)
    app.router.add_route('POST', '/result', call_result)
    
    for route in list(app.router.routes()):
        cors.add(route)
        
    web.run_app(app, port=os.environ.get('PORT', ''))


if __name__ == "__main__":
    main()    
