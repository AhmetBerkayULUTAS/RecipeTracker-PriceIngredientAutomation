"""
Düzgün Çalışmıyor !! basit arama yapılıyor en son bakılıcak
"""
import pickle
import tensorflow as tf
from transformers import AutoTokenizer
import numpy as np
import os # PATH kontrolü için

try:
    from config.settings import MODEL_PATH, VECTORIZER_PATH, SCALER_PATH, TFLITE_MODEL_PATH
except ImportError:
    print("Uyarı: config/settings.py bulunamadı. Model yolları varsayılan değerlere ayarlanıyor.")
    MODEL_PATH = "models/model.pkl"
    VECTORIZER_PATH = "models/vectorizer.pkl"
    SCALER_PATH = "models/scaler.pkl"
    TFLITE_MODEL_PATH = "models/all-MiniLM-L6-v2.tflite"


class MLModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            
            cls._instance = super(MLModelManager, cls).__new__(cls)
            
            cls._instance._load_models()
       
        return cls._instance

    def _load_models(self):
       
        self.ml_model = None
        self.vectorizer = None
        self.scaler = None
        self.tflite_embedder_interpreter = None
        self.tflite_embedder_tokenizer = None
        self.tflite_input_details = None
        self.tflite_output_details = None

        print("--- Modeller Yükleniyor ---")

        # --- Naive Bayes Modeli ve Diğer Bileşenlerin Yüklenmesi ---
        try:
            if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH) or not os.path.exists(SCALER_PATH):
                raise FileNotFoundError("Naive Bayes modeli veya yardımcı dosyaları bulunamadı.")
            
            with open(MODEL_PATH, 'rb') as f:
                self.ml_model = pickle.load(f)
            with open(VECTORIZER_PATH, 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(SCALER_PATH, "rb") as f:
                self.scaler = pickle.load(f)
            print("model, vektörleştirici ve scaler başarıyla yüklendi.")
        except FileNotFoundError as e:
            print(f"Hata: model yüklenirken dosya bulunamadı: {e}. Lütfen '{os.path.dirname(MODEL_PATH)}' dizinindeki model dosyalarını kontrol edin.")
        except Exception as e:
            print(f"Hata: modeller veya scaler yüklenirken genel bir hata oluştu: {e}")
        
        # --- TFLite Embedding Modeli ve Tokenizer'ın Yüklenmesi ---
        try:
            if not os.path.exists(TFLITE_MODEL_PATH):
                raise FileNotFoundError("TFLite modeli bulunamadı.")
                
            self.tflite_embedder_interpreter = tf.lite.Interpreter(model_path=str(TFLITE_MODEL_PATH))
            self.tflite_embedder_interpreter.allocate_tensors()

            self.tflite_input_details = self.tflite_embedder_interpreter.get_input_details()
            self.tflite_output_details = self.tflite_embedder_interpreter.get_output_details()

            self.tflite_embedder_tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

            print("TFLite embedding modeli ve tokenizer başarıyla yüklendi.")
        except FileNotFoundError as e:
            print(f"Hata: TFLite model yüklenirken dosya bulunamadı: {e}. Lütfen '{os.path.dirname(TFLITE_MODEL_PATH)}' dizinindeki model dosyasını kontrol edin.")
        except Exception as e:
            print(f"Hata: TFLite embedding modeli veya tokenizer yüklenirken genel bir hata oluştu: {e}")

    def are_models_loaded(self):
        return (self.ml_model is not None and
                self.vectorizer is not None and
                self.scaler is not None and
                self.tflite_embedder_interpreter is not None and
                self.tflite_embedder_tokenizer is not None)

