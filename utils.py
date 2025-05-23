import requests
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


def get_baskets_json(url: str = 'http://basket-10c.dp.wb.ru:8080/shardes_v3',
                     timeout_secs: float = 10.) -> dict:
    """
    Формирует JSON-файл с информацией о бакетах и vol на них.
    :param url: url API, которая возвращает состояние всех существующих бакетов.
    :param timeout_secs: время ожидания ответа от API.
    :return: распаршенный JSON-файл.
    """
    response = requests.get(url, timeout=timeout_secs)
    if response.status_code != 200:
        raise ValueError(f'Request failed with status code: {response.status_code}.')

    return response.json()


def create_basket_path(item_id: int,
                       idx: int = 1,
                       basket_json: dict = None,
                       url: str = None
                       ) -> str:
    """
    Формирует URL картинки по nm.

    :param item_id: артикул товара (nm).
    :param idx: порядковый номер картинки товара.
    :param basket_json: распаршенный JSON-файл с текущим состоянием о бакетах
    :param url: url API, которая возвращает состояние о всех существующих бакетов.
    :return: URL картинки.
    """
    if basket_json is None:
        basket_json = get_baskets_json() if url is None else get_baskets_json(url=url)

    vol, part_id = item_id // 100_000, item_id // 1_000

    for k in basket_json.keys():
        if basket_json[k]['minVol'] <= vol <= basket_json[k]['maxVol']:
            basket_name = k.split('.')[0]

            basket_path = "http://{}.wbbasket.ru/vol{}/part{}/{}/images/big/{}.webp".format(
                basket_name, vol, part_id, item_id, idx
            )

            return basket_path

    raise ValueError('Unexpected nm.')


def download_image(url: str) -> Image:
    """
    Загружает картинку по URL.
    :param url: URL картинки.
    :return: PIL.Image
    """
    response = requests.get(url, timeout=10.)
    if response.status_code != 200:
        raise ValueError(f'Request failed with status code: {response.status_code}.')

    return Image.open(BytesIO(response.content))


def get_images(nmids: list, basket_json: dict = None) -> dict:
    """
    Загружает изображения по списку nmids.
    :param basket_json: инфо о состоянии бакетов.
    :param nmids: список артикулов.
    :return: словарь nmids: images
    """
    images = {}

    if basket_json is None:
        basket_json = get_baskets_json()

    nmid_paths = {nm: create_basket_path(nm, basket_json=basket_json) for nm in nmids}

    with ThreadPoolExecutor() as executor:
        futures = {nmid: executor.submit(download_image, path) for nmid, path in nmid_paths.items()}

        for nmid, future in futures.items():
            images[nmid] = future.result()

    return images
