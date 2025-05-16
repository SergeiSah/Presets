import io
import zipfile
import requests
import pandas as pd
import streamlit as st
from pathlib import Path
from PIL import Image

from utils import get_images


# === НАСТРОЙКИ ===
ZIP_URL = "https://github.com/SergeiSah/Presets/releases/download/0.0.1/images.zip"
DATA_DIR = Path("data")
DESCRIPTION_FILE = "description.pq"
CLUSTERS_INFO_FILE = "clusters_info.pq"
COLUMNS = 5
IMAGE_HEIGHT = 250
cluster_names = {
    1: "Cluster 1",
    2: "Cluster 2",
}


# === ЗАГРУЗКА МЕТАДАННЫХ ===
@st.cache_data
def load_data(file):
    return pd.read_parquet(DATA_DIR / file)


# === ОСНОВНОЙ КОД ===
def main():
    st.set_page_config(layout="wide")
    st.title("Просмотр изображений по кластерам")

    desc = load_data(DESCRIPTION_FILE)
    clusters_info = load_data(CLUSTERS_INFO_FILE)

    clusters = clusters_info.set_index('cluster_name')['cluster_id'].to_dict()

    selected_cluster = st.selectbox("Выберите кластер", list(clusters.keys()))
    cluster_id = clusters[selected_cluster]

    cluster_df = desc.query('cluster_id == @cluster_id')
    nmids = cluster_df.index.tolist()

    # Получаем имена файлов изображений в выбранной папке
    cluster_images = get_images(nmids)

    # Извлекаем ID из имён
    cluster_df = desc[desc.index.isin(nmids)]

    st.header(f"Изображения для кластера '{selected_cluster}'")
    rows = len(cluster_images) // COLUMNS + len(cluster_images) % COLUMNS

    for i, (nmid, image) in enumerate(cluster_images.items()):
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