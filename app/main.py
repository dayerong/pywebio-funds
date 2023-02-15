#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from routers import pywebio_stocks, pywebio_funds
from pywebio.platform.fastapi import asgi_app

app = FastAPI()
enter_app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@enter_app.get("/", response_class=RedirectResponse)
def root() -> RedirectResponse:
    response = RedirectResponse(url="/index/", status_code=302)
    return response


add_stocks = asgi_app(pywebio_stocks.add_stock)
query_stocks = asgi_app(pywebio_stocks.query_stock)
add_funds = asgi_app(pywebio_funds.add_fund)
query_funds = asgi_app(pywebio_funds.query_fund)
index = asgi_app(pywebio_funds.index)

app.mount("/add/stocks", add_stocks)
app.mount("/query/stocks", query_stocks)
app.mount("/add/funds", add_funds)
app.mount("/query/funds", query_funds)
app.mount("/index", index)
app.mount("/", enter_app)

if __name__ == '__main__':
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    uvicorn.run(app='main:app',
                host="0.0.0.0",
                port=8080,
                reload=False,
                debug=True,
                proxy_headers=True,
                log_config=log_config)