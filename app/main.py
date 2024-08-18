import json
import os
import time

from redis.commands.search.field import TextField, TagField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from app import app
from flask import session, render_template, request, redirect, url_for
from connection import RedisConnection
from generator import load_data
import logging


@app.template_filter()
def currencyFormat(value):
    value = float(value)
    return "${:,.2f}".format(value)


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    try:
        _quantity = int(request.form['quantity'])
        _code = request.form['code']
        if _quantity and _code and request.method == 'POST':
            qry = f"@sku:{_code}"
            print("Generated query string: " + qry)
            query = Query(qry)
            print(f"Trying to add the product to the cart with Redis status {conn.ping()}")
            docs = conn.ft("idx_product").search(query).docs
            doc = json.loads(docs[0].json)
            itemArray = {
                doc['sku']: {'name': doc['name'],
                          'code': doc['sku'],
                          'quantity': _quantity,
                          'price': doc['price'],
                          'image': doc['image'],
                          'total_price': _quantity * doc['price']}
            }

            sub_total_price = 0
            sub_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:
                if doc['sku'] in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if doc['sku'] == key:
                            current_quantity = session['cart_item'][key]['quantity']
                            total_quantity = current_quantity + _quantity
                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * doc['price']
                else:
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    sub_total_quantity = sub_total_quantity + individual_quantity
                    sub_total_price = sub_total_price + individual_price
            else:
                session['cart_item'] = itemArray
                sub_total_quantity = sub_total_quantity + _quantity
                sub_total_price = sub_total_price + _quantity * doc['price']

            session['sub_total_quantity'] = sub_total_quantity
            session['sub_total_price'] = sub_total_price

            return redirect(url_for('.products'))
        else:
            return 'Error while adding item to cart'
    except Exception as e:
        print(e)


@app.route('/')
def products():
    #########################################
    ##
    ## Query used:
    ## ft.search idx_product "@name:puma | @brand:{puma}" limit 0 100
    ##
    #########################################
    search_param = request.args.get("search_param")
    qry = "*"
    if search_param:
        qry = f"@name:*{search_param}*" + " | @brand:{"+search_param+"}"
    else:
        search_param = ''

    print("Generated query string: " + qry)
    query = (Query(qry).paging(0, 100))
    time1 = time.time()
    docs = conn.ft("idx_product").search(query).docs
    time2 = time.time()
    print(f"Product list retrieved in {(time2 - time1):.3f} seconds")

    result = []
    for doc in docs:
        result.append(json.loads(doc.json))

    return render_template('products.html', products=result, search_param=search_param, region=region)


@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        sub_total_price = 0
        sub_total_quantity = 0
        session.modified = True

        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        sub_total_quantity = sub_total_quantity + individual_quantity
                        sub_total_price = sub_total_price + individual_price
                break

        if sub_total_quantity == 0:
            session.clear()
        else:
            session['sub_total_quantity'] = sub_total_quantity
            session['sub_total_price'] = sub_total_price

        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


def createIndexes():
    try:
        # FT.CREATE idx_product on JSON PREFIX 1 "product:"
        # SCHEMA
        #   $.name as name TEXT
        #   $.description as description TEXT
        #   $.brand as brand TAG
        #   $.price as price NUMERIC SORTABLE
        #   $.sku as sku TEXT
        schema = (TextField("$.name", as_name="name"),
                  TextField("$.description", as_name="description"),
                  TagField("$.brand", as_name="brand"),
                  NumericField("$.price", as_name="price", sortable=True),
                  TextField("$.sku", as_name="sku"))
        conn.ft("idx_product").create_index(schema, definition=IndexDefinition(prefix=["product:"],index_type=IndexType.JSON))
    except Exception as inst:
        logging.error("Exception occurred while creating indexes")

if __name__ == "__main__":
    region = os.getenv('REGION', "LOCAL")
    conn = RedisConnection().get_connection()
    createIndexes()
    load_data()
    app.run(host='0.0.0.0', debug=True, port=5555)
