######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Shopcart Steps
Steps file for Shopcarts.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect


@given("the following shopcarts")
def step_impl(context):
    """Delete all Shop carts and load new ones"""
    # List all of the shop carts and delete them one by one
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for shopcart in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{shopcart['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new shopcarts and items
    for row in context.table:
        payload = {"customer_id": row["customer_id"], "items": []}
        resp = requests.post(rest_endpoint, json=payload)
        expect(resp.status_code).to_equal(201)


@given("the following items")
def step_impl(context):
    rest_endpoint = f"{context.base_url}/shopcarts"
    for row in context.table:
        resp = requests.get(rest_endpoint + "?customer_id=" + row["customer_id"])
        expect(resp.status_code).to_equal(200)
        data = resp.json()
        shopcart_id = data[0]["id"]
        payload = {
            "name": row["name"],
            "quantity": row["quantity"],
            "description": row["description"],
            "price": row["price"],
            "shopcart_id": shopcart_id,
        }
        resp = requests.post(
            rest_endpoint + "/" + str(shopcart_id) + "/items", json=payload
        )
        expect(resp.status_code).to_equal(201)
