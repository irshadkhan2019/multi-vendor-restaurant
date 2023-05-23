import datetime


def generateOrderNumber(pk):
    current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    order_number = current_datetime + str(pk)
    return order_number
