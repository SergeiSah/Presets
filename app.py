import pandas as pd
import streamlit as st
from PIL import Image
import zipfile
import requests
import io

# === НАСТРОЙКИ ===
ZIP_URL = "https://github.com/SergeiSah/Presets/releases/download/0.0.1/images.zip"
DESCRIPTION_FILE = "description.pq"
COLUMNS = 5
IMAGE_HEIGHT = 250


# === КЕШИРУЕМ ЗАГРУЗКУ ZIP-ФАЙЛА ===
@st.cache_resource
def load_zip_from_github():
    response = requests.get(ZIP_URL)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    return zip_file


# === ЗАГРУЗКА МЕТАДАННЫХ ===
@st.cache_data
def load_data():
    return pd.read_parquet(DESCRIPTION_FILE)


# === ОСНОВНОЙ КОД ===
def main():
    st.set_page_config(layout="wide")
    st.title("Просмотр изображений по кластерам")

    df = load_data()
    zip_file = load_zip_from_github()
    # zip_file = zipfile.ZipFile("images.zip")

    # Автоматическое определение кластеров по папкам в архиве
    folders = sorted(set(p.split('/')[0] for p in zip_file.namelist() if '/' in p))
    clusters = {f"Cluster {i+1}": f for i, f in enumerate(folders)}

    selected_cluster = st.selectbox("Выберите кластер", list(clusters.keys()))
    cluster_folder = clusters[selected_cluster]

    # Получаем имена файлов изображений в выбранной папке
    cluster_images = sorted([
        f for f in zip_file.namelist()
        if f.startswith(f"{cluster_folder}/") and f.lower().endswith((".jpg", ".png", ".jpeg"))
    ])

    # Извлекаем ID из имён
    nmids = [int(f.split("/")[-1].split(".")[0]) for f in cluster_images]
    cluster_df = df[df.index.isin(nmids)]

    st.header(f"Изображения для кластера '{selected_cluster}'")

    rows = [cluster_images[i:i + COLUMNS] for i in range(0, len(cluster_images), COLUMNS)]

    for row in rows:
        cols = st.columns(COLUMNS)
        for idx, zip_img_path in enumerate(row):
            nmid_img = zip_img_path.split("/")[-1]
            nmid = int(nmid_img.split(".")[0])

            with cols[idx]:
                # Данные о товаре
                if nmid in cluster_df.index:
                    item_info = cluster_df.loc[nmid]
                    title = item_info.get('title', 'Нет названия')
                    subject = item_info.get('subjectname', 'Нет категории')
                else:
                    title = "Нет данных"
                    subject = "Нет данных"

                try:
                    with zip_file.open(zip_img_path) as img_file:
                        image = Image.open(img_file)
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