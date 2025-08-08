"""convert_embedding_model_to_tflite.py

Bu betik, bir SentenceTransformer modelini (PyTorch tabanlı) TensorFlow Keras modeline dönüştürür
ve ardından onu TFLite formatına aktarır.

MODEL DÜZGÜN ÇALIŞMIYOR!!!! basit arama yapılıyor en son tekrardan bakılıcak !!!!!!
"""

import torch
import tensorflow as tf
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, TFAutoModel 
import os
import shutil


OUTPUT_DIR = "models"
os.makedirs(OUTPUT_DIR, exist_ok=True)


model_name = "all-MiniLM-L6-v2"

tflite_model_path = os.path.join(OUTPUT_DIR, f"{model_name}.tflite")

def convert_sentence_transformer_to_tflite_direct_tf(model_id, output_tflite_path, max_seq_length=128):


    local_pt_model_path = os.path.join(OUTPUT_DIR, f"{model_name}_pytorch_local")
    tf_saved_model_path = os.path.join(OUTPUT_DIR, f"{model_name}_tf_saved_model_direct")

    try:
        print(f"1. {model_id} SentenceTransformer modelini yüklüyor ve yerel olarak kaydediyor...")
        st_model = SentenceTransformer(model_id)
        print("Model yüklendi.")

        st_model.save_pretrained(local_pt_model_path)
        print(f"PyTorch modeli ve tokenizer yerel olarak kaydedildi: {local_pt_model_path}")

        print("2. Yerel PyTorch modelini doğrudan TensorFlow Keras modeline dönüştürüyor (Hugging Face Transformers ile)...")

        tf_model = TFAutoModel.from_pretrained(local_pt_model_path, from_pt=True)
        print("PyTorch modeli doğrudan TensorFlow Keras modeline dönüştürüldü.")


        tf_model.save(tf_saved_model_path, save_format="tf")
        print(f"TensorFlow modeli SavedModel formatına kaydedildi: {tf_saved_model_path}")

        print("3. TensorFlow SavedModel modelini TFLite formatına dönüştürüyor...")
        converter = tf.lite.TFLiteConverter.from_saved_model(tf_saved_model_path)

        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS, 
            tf.lite.OpsSet.SELECT_TF_OPS    
        ]

        def representative_dataset_gen():
            for _ in range(1): 
                yield {
                    "input_ids": tf.random.uniform(shape=[1, max_seq_length], minval=0, maxval=st_model.tokenizer.vocab_size, dtype=tf.int32),
                    "attention_mask": tf.ones(shape=[1, max_seq_length], dtype=tf.int32),
                    "token_type_ids": tf.zeros(shape=[1, max_seq_length], dtype=tf.int32) 
                }
        converter.representative_dataset = representative_dataset_gen

        tflite_model_content = converter.convert()

        with open(output_tflite_path, 'wb') as f:
            f.write(tflite_model_content)
        print(f"Model TFLite formatına dönüştürüldü ve kaydedildi: {output_tflite_path}")
        return True

    except Exception as e:
        print(f"Model dönüştürülürken bir hata oluştu: {e}")
        return False
    finally:
        if os.path.exists(tf_saved_model_path):
            try:
                shutil.rmtree(tf_saved_model_path)
                print(f"Geçici SavedModel klasörü silindi: {tf_saved_model_path}")
            except OSError as e:
                print(f"Geçici SavedModel klasörü silinirken hata oluştu: {e}")
        if os.path.exists(local_pt_model_path):
            try:
                shutil.rmtree(local_pt_model_path)
                print(f"Geçici PyTorch yerel klasörü silindi: {local_pt_model_path}")
            except OSError as e:
                print(f"Geçici PyTorch yerel klasörü silinirken hata oluştu: {e}")

if __name__ == "__main__":

    print("--- TFLite Model Dönüştürme Başlatılıyor ---")
    success = convert_sentence_transformer_to_tflite_direct_tf(model_name, tflite_model_path)
    if success:
        print("\nDönüştürme başarıyla tamamlandı. Artık TFLite modelini kullanabilirsiniz.")
        print(f"TFLite modeli şuraya kaydedildi: {tflite_model_path}")
    else:
        print("\nDönüştürme başarısız oldu. Lütfen yukarıdaki hata mesajlarını kontrol edin ve ortam kurulumunuzu gözden geçirin.")
