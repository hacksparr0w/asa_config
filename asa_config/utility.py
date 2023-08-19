def find(predicate, iterable):
    for index, item in enumerate(iterable):
        if predicate(item):
            return index, item

    return None
