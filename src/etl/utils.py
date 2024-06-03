HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "es-ES,es;q=0.9",
    "Access-Control-Request-Headers": "deviceos,mpid,x-appversion,x-deviceid,x-deviceos",
    "Access-Control-Request-Method": "GET",
    "Connection": "keep-alive",
    "Origin": "https://es.wallapop.com",
    "Referer": "https://es.wallapop.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

URLS = {
    "categories": "https://api.wallapop.com/api/v3/categories",
    "users": "https://api.wallapop.com/api/v3/users/{user_id}",
    "user_reviews": "https://api.wallapop.com/api/v3/users/{user_id}/reviews?init=0",
    "user_items": "https://api.wallapop.com/api/v3/users/{user_id}/items",
    "item": "https://api.wallapop.com/api/v3/items/{item_id}?language=es",
    "search": "https://api.wallapop.com/api/v3/general/search",
}

RECURSION_LIMIT = 1000
