import os
import pickle
import pandas as pd
import sys
import time

from flask import Flask, request, Response
from rossmann.Rossmann import Rossmann


def log(msg):
    # print + flush garante que a linha aparece IMEDIATAMENTE nos logs do Render
    # (sem flush, o Python pode bufferizar e você só veria tudo de uma vez no final)
    print(f"[BOOT] {msg}", flush=True)

t0 = time.time()
log("iniciando handler.py")
log(f"python version: {sys.version}")
log(f"cwd: {os.getcwd()}")
log(f"arquivos na raiz: {os.listdir('.')}")

log("carregando modelo...")
#loading model
model = pickle.load( open('model/model_rossmann.pkl', 'rb'))
log(f"modelo carregado em {time.time() - t0:.2f}s")

log("inicializando Flask app...")
#initialize API
app = Flask(__name__)
log("Flask app criado")

@app.route( '/rossmann/predict', methods=['POST'] )
def rossmann_predict():
    test_json = request.get_json()
    
    if test_json: # sehouver dados
        try:
            if isinstance( test_json, dict ): # unique example
                test_raw = pd.DataFrame( test_json, index=[0] )
            else: # multiple example
                test_raw = pd.DataFrame( test_json, columns=test_json[0].keys() )

            # Instantiate Rossmann class
            pipeline = Rossmann()

            # data cleaning
            df1 = pipeline.data_cleaning( test_raw )

            # feature engineering
            df2 = pipeline.feature_engineering( df1 )

            # data preparation
            df3 = pipeline.data_preparation( df2 )

            # prediction
            df_response = pipeline.get_prediction( model, test_raw, df3 )

            return df_response
        
        except Exception as e:
            return Response(
                response=str(e),
                status=500,
                mimetype='application/json'
            )
    
    else:
        return Response( '{}', status=200, mimetype='application/json' )
    
# rota simples para o Render confirmar que o serviço está de pé
@app.route('/', methods=['GET'])
def health():
    return Response('ok', status=200)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    log(f"chamando app.run na porta {port}")
    app.run(host='0.0.0.0', port=port)
