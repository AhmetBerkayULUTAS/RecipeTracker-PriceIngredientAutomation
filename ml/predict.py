"""
Düzgün Çalışmıyor !! basit arama yapılıyor en son bakılıcak
"""

import numpy as np
from scipy.sparse import hstack, csr_matrix
import tensorflow as tf
from ml.model_manager import MLModelManager
from ml.preprocess import clean_text

def is_relevant(search_query: str, product_name: str) -> bool:
    models = MLModelManager()

    if not models.are_models_loaded():
        print("Uyarı: Gerekli ML/TFLite bileşenleri tam olarak yüklenemedi. Basit arama yapılıyor.")
        return search_query.lower() in product_name.lower()

    
    cleaned_product_name = clean_text(product_name)

    # --- 1. TF-IDF Vektörleştirme ---
    vectorized_name = models.vectorizer.transform([cleaned_product_name])

    # --- 2. TFLite Embedder ile Gömme (Embedding) ---
    max_seq_len = models.tflite_input_details[0]['shape'][1] 
    if max_seq_len == -1: 
        max_seq_len = 128 
        print(f"Uyarı: TFLite modeli dinamik input uzunluğuna sahip. '{max_seq_len}' sabit uzunluk kullanılıyor.")

    inputs = models.tflite_embedder_tokenizer(
        cleaned_product_name,
        return_tensors="tf",
        padding='max_length',
        truncation=True,
        max_length=max_seq_len
    )

    input_ids_tensor = tf.cast(inputs['input_ids'], models.tflite_input_details[0]['dtype'])
    attention_mask_tensor = tf.cast(inputs['attention_mask'], models.tflite_input_details[1]['dtype'])

    models.tflite_embedder_interpreter.set_tensor(models.tflite_input_details[0]['index'], input_ids_tensor)
    models.tflite_embedder_interpreter.set_tensor(models.tflite_input_details[1]['index'], attention_mask_tensor)
    

    models.tflite_embedder_interpreter.invoke()


    X_embed_raw = models.tflite_embedder_interpreter.get_tensor(models.tflite_output_details[0]['index'])
    
    # --- Pooling işlemi (Mean Pooling) ---
    input_mask_expanded = np.expand_dims(inputs['attention_mask'], -1).astype(float)
    
    sum_embeddings = np.sum(X_embed_raw * input_mask_expanded, 1)
    
    sum_mask = np.maximum(np.sum(input_mask_expanded, 1), 1e-9) 
    
    X_embed = sum_embeddings / sum_mask

    # --- 3. Gömme Vektörlerini Ölçekle (Scaler) ---
    X_embed_scaled = models.scaler.transform(X_embed)

    # --- 4. TF-IDF ve Gömme Vektörlerini Birleştir ---
    X_combined = hstack([vectorized_name, csr_matrix(X_embed_scaled)])

    # --- 5. Naive Bayes Modeli ile Tahmin Yap ---
    return models.ml_model.predict(X_combined)[0] == 1