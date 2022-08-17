from aiohttp import web
import aiohttp_cors

import os
import json
import uuid
from datetime import datetime as dt
import logging
import time


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

async def call_upload(request):
    request_str = json.loads(str(await request.text()))
    requested_files = json.loads(request_str)
    upscaled_path = './data/upscaled/'
    files = os.listdir(upscaled_path)
    # HARD CODE
    JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI4YmFmYTI3Mi05YTdjLTRhYmYtOWM2Yi04N2QxNzYwZmRiNWMiLCJlbWFpbCI6InN1cGF3YXRAaW50ZWxlay5haSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImlkIjoiRlJBMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfSx7ImlkIjoiTllDMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiI2MTE5ODVhOTNlYTViMDk1NGFhMCIsInNjb3BlZEtleVNlY3JldCI6Ijg5YWUwZTcwMmFkZmM3ZDA4ZGU1N2Q1M2M2ZGYyYmZiZDcwYmE0MmZkY2E2NTdlOTIyZDZmM2E1Yjk1OGVhYjYiLCJpYXQiOjE2NjA3NjU2MTR9.u8gByuVBa2bsH9sa2BLh2Bb0NunLqG0ZaqQZTZnvwHw"
    URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
      'Authorization': f'Bearer {JWT}'
    }
    URIs = []
    for requested_file in sorted(requested_files):
        file_path = upscaled_path + requested_file
        payload={'pinataOptions': '{"cidVersion": 1}',
                 'pinataMetadata': '{"name": "test", 
                 "keyvalues": {"company": "autoNFT"}}'}
        files=[
          ('file', (requested_file, open(file_path,'rb'),'application/octet-stream'))
        ]
        response = requests.request("POST", url,
                                            headers=headers, data=payload, files=files)
        URIs.append(response.text)
    
    return web.Response(text=json.dumps(URIs), content_type="text/html")

async def call_result(request):
    request_str = json.loads(str(await request.text()))
    requested_file_name = json.loads(request_str)
    logger.info("call_result filename: {}".format(requested_file_name))
    upscaled_path = './data/upscaled/'
    files = os.listdir(upscaled_path)
    # check if file with name filename* in 'data/generated' folder
    for file_name in sorted(files):
        if file_name.startswith(requested_file_name):
            time.sleep(1)
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
    app.router.add_route('POST', '/upload', call_upload)
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*")
        }
    )
    
    for route in list(app.router.routes()):
        cors.add(route)
        
    web.run_app(app, port=os.environ.get('PORT', ''))


if __name__ == "__main__":
    main()    
