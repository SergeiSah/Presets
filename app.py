import io
import requests
import pandas as pd
import streamlit as st
from PIL import Image

from utils import get_images, get_baskets_json


# === НАСТРОЙКИ ===
DESCRIPTION_URL = "https://github.com/SergeiSah/Presets/releases/download/v0.0.2/description.pq"
CLUSTERS_INFO_URL = "https://github.com/SergeiSah/Presets/releases/download/v0.0.2/clusters_info.pq"
COLUMNS = 5
IMAGE_HEIGHT = 250


# === ЗАГРУЗКА МЕТАДАННЫХ ===
@st.cache_data
def load_data(file_url):
    file = io.BytesIO(requests.get(file_url).content)
    return pd.read_parquet(file)


@st.cache_data
def load_basket_json(url: str = 'http://basket-10c.dp.wb.ru:8080/shardes_v3'):
    return get_baskets_json(url)


# === ОСНОВНОЙ КОД ===
def main():
    st.set_page_config(layout="wide")
    st.title("Просмотр изображений по кластерам")

    desc = load_data(DESCRIPTION_URL)
    clusters_info = load_data(CLUSTERS_INFO_URL)
    basket_json = load_basket_json()

    clusters = clusters_info.set_index('cluster_name')['cluster_id'].to_dict()

    selected_cluster = st.selectbox("Выберите кластер", list(clusters.keys()))
    cluster_id = clusters[selected_cluster]

    cluster_df = desc.query('cluster_id == @cluster_id')
    nmids = cluster_df.index.tolist()

    # cluster_images = get_images(nmids)
    cluster_df = desc[desc.index.isin(nmids)]

    st.header(f"Изображения для кластера '{selected_cluster}'")

    # for i, (nmid, image) in enumerate(cluster_images.items()):
    for i, nmid in enumerate(nmids):
        if i % COLUMNS == 0:
            cols = st.columns(COLUMNS)

        image = get_images([nmid], basket_json)[nmid]

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