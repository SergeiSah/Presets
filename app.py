import io
import json
import requests
import pandas as pd
import streamlit as st
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

from utils import get_images, download_image, create_basket_path


# === НАСТРОЙКИ ===
DESCRIPTION_URL = "https://github.com/SergeiSah/Presets/releases/download/v0.0.2/description.pq"
CLUSTERS_INFO_URL = "https://github.com/SergeiSah/Presets/releases/download/v0.0.2/clusters_info.pq"
COLUMNS = 5
IMAGE_HEIGHT = 250


# === ЗАГРУЗКА МЕТАДАННЫХ ===
@st.cache_data
def load_data(file_url):
    response = requests.get(file_url, timeout=10.)

    if response.status_code != 200:
        raise ValueError(f'Request failed with status code: {response.status_code}.')

    file = io.BytesIO(response.content)
    return pd.read_parquet(file)


@st.cache_data
def load_basket_json():
    with open('data/basket.json') as f:
        basket_json = json.load(f)
    return basket_json


# === ОСНОВНОЙ КОД ===
def main():
    st.set_page_config(layout="wide")
    st.title("Просмотр изображений по кластерам")

    desc = load_data(DESCRIPTION_URL)
    clusters_info = load_data(CLUSTERS_INFO_URL)
    basket_json = load_basket_json()

    clusters_info['cluster_name'] = clusters_info.apply(lambda x: f"{x['cluster_id']}. {x['cluster_name']}", axis=1)
    clusters = (
        clusters_info
        .sort_values('cluster_id')
        .set_index('cluster_name')['cluster_id'].to_dict()
    )

    selected_cluster = st.selectbox("Выберите кластер", list(clusters.keys()))
    cluster_id = clusters[selected_cluster]

    cluster_df = desc.query('cluster_id == @cluster_id')
    nmids = cluster_df.index.tolist()
    nmid_paths = {nm: create_basket_path(nm, basket_json=basket_json) for nm in nmids}

    # cluster_images = get_images(nmids)
    cluster_df = desc[desc.index.isin(nmids)]

    st.header(f"Изображения для кластера '{selected_cluster}'")
    # images = get_images(nmids, basket_json)

    # for i, (nmid, image) in enumerate(cluster_images.items()):
    for i, nmid in enumerate(nmids):
        if i % COLUMNS == 0:
            cols = st.columns(COLUMNS)

        with cols[i % COLUMNS]:

            # Данные о товаре
            if nmid in cluster_df.index:
                item_info = cluster_df.loc[nmid]
                title = item_info.get('title', 'Нет названия')
                subject = item_info.get('subjectname', 'Нет категории')
            else:
                title = "Нет данных"
                subject = "Нет данных"

            try:
                image = download_image(nmid_paths[nmid])
                width, height = image.size
                new_width = int(width * (IMAGE_HEIGHT / height))
                resized_image = image.resize((new_width, IMAGE_HEIGHT))
                st.image(resized_image)

                st.markdown(f"""
                <div style='margin-top: 10px; line-height: 1.4;'>
                    <strong>{title}</strong><br>
                    <small>Категория: {subject}</small><br>
                    <small>ID: {nmid}</small>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error("Ошибка загрузки изображения")
                st.image(Image.new('RGB', (150, IMAGE_HEIGHT), color='gray'))


if __name__ == "__main__":
    main()