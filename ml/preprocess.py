import re
import pickle
import tensorflow as tf
import numpy as np
from transformers import AutoTokenizer


from config.settings import MODEL_PATH, VECTORIZER_PATH, SCALER_PATH, TFLITE_MODEL_PATH


def clean_text(text):
    text = str(text).lower()

    text = re.sub(r'\(.*?\)', '', text)  #parantez kaldır 

    birimler_ve_gereksizler = [
        'kg', 'g', 'gr', 'ml', 'l', 'lt', 'cc', 'cl', 'pcs',
        'li', 'lı', 'lu', 'lü', 'lik', 'lık', 'luk', 'lük', 
        'su bardağı', 'çay bardağı', 'yemek kaşığı', 'tatlı kaşığı', 'çay kaşığı',
        'kaşık', 'bardak', 'bardağı', 'adet', 'gram', 'paket', 'çimdik', 'fincan', 'tane', 'diş',
        'biraz', 'az', 'büyük', 'küçük', 'orta', 'isteğe bağlı', 'isteğe',
        'gerektiği kadar', 'göz kararı', 'yarım', 'çeyrek', 'bütün', 'silme',
        'kutu', 'sıcak', 'soğuk', 'elenmiş', 'poşet', 'yaklaşık', 'kadar', 'kase', 'rende', 'küp',
        'kıyılmış', 'doğranmış', 'iri', 'ince', 'dilimlenmiş', 'soyulmuş', 'kabuklu', 'kabuksuz',
        'kavrulmuş', 'kızartılmış', 'haşlanmış', 'kızarmış', 'pişirilmiş', 'taze', 'kuru', 'yumuşak', 'sert',
        'süzme', 'süzülmüş', 'süzgeçten geçirilmiş',
        'rendelenmiş',
        'iri doğranmış', 'ince doğranmış', 'tepeleme',
        'kıyma','damak tadına göre', 'damak zevkine göre'
    ]
    
    pattern = r'[\d,.]*\s*(' + '|'.join(birimler_ve_gereksizler) + r')\b'
    text = re.sub(pattern, '', text)
    
    text = re.sub(r'[\d,.]+', '', text)    # Sayı ve ondalık ayıraçları
    text = re.sub(r'[^\w\s-]', '', text)     # Harf, sayı, boşluk ve tire DIŞINDAKİ her şey
    
    text = re.sub(r'\s+', ' ', text).strip()

    return text


