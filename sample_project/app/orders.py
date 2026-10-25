from fastapi import FastAPI


app = FastAPI()


@app.route("/orders")
def get_orders():
    return "Orders list"