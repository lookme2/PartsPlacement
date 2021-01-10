from inventree.api import InvenTreeAPI
from inventree.part import Part
from inventree.stock import StockItem
import inventree


SERVER_ADDRESS = 'http://172.16.1.44:8000'
# My_USERNAME = 'bench'
# MY_PASSWORD = 'solderBench1!'
My_TOKEN = '7b8172e38efa1585f69cc6862b7e01f4d6a5b7d3'

# my_part = None
# part_count = None
# search_number = "STM32F100V8T6B"

# api = InvenTreeAPI(SERVER_ADDRESS, username=My_USERNAME, password=MY_PASSWORD)


def find_part_location(part_number):
    """
    find part location in database
    :param part_number: part number to find
    :return: location of the part
    """
    try:
        api = InvenTreeAPI(SERVER_ADDRESS, token=My_TOKEN, verbose=True)
        parts = Part.list(api, search=part_number)
        # print(len(parts))

        if len(parts) == 1:
            my_part = parts[0].pk
        elif len(parts) > 1:
            for part in parts:
                my_part = part.pk  # get internal part number
                part_count = part._data['in_stock']  # total qty in stock

        part = Part(api, my_part)
        stock_items = part.getStockItems()
        if stock_items:
            if stock_items[0]._data['location']:
                stock_location = stock_items[0]._data['location']
                location = inventree.stock.StockLocation(api, pk=stock_location)
                my_location = location._data['name']
            else:
                my_location = 'No Location'
        # print(my_location)
        return my_location
    except:
        print(api)
        print('Can not connect to the database')
