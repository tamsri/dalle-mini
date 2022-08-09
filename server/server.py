from aiohttp import web
import os
import json


async def call_test(request):
    content = "get ok"
    return web.Response(text=content, content_type="text/html")


async def call_request(request):
    request_str = json.loads(str(await request.text()))
    data = json.loads(request_str)
    result = (data['text_a'], data['text_b'])
    answer = 'request_received'
    return web.Response(text=answer, content_type="text/html")


def main():
    app = web.Application(client_max_size=1024**3)
    app.router.add_route('GET', '/test', call_test)
    app.router.add_route('POST', '/request', call_request)
    web.run_app(app, port=os.environ.get('PORT', ''))


if __name__ == "__main__":
    main()
