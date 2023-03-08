import logging
import azure.functions as func
from keybert import KeyBERT
import json
import os

MODEL = os.getenv('MODEL', 'all-MiniLM-L6-v2')
MAX_TOKENS = os.getenv('MAX_TOKENS', 2)
USE_NMR = os.getenv('USE_NMR', 'True')[0] in ['T', 't']
kw_model = KeyBERT(model = MODEL)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    keys = ('title', 'description', 'body')
    document_pieces = []
    for key in keys:
        value = req.params.get(key)
    
        if not value:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                value = req_body.get(key)
        if value:
            document_pieces.append(value)
    document = ' '.join(document_pieces)
    document = document.strip()

    logging.debug(f'Extract keywords from {document}')
    if document:
        keywords = kw_model.extract_keywords(document, keyphrase_ngram_range = (1, MAX_TOKENS), use_mmr = USE_NMR, top_n = 3)
        response = [{'keyword': kw[0], 'distance': kw[1]} for kw in keywords]
        return func.HttpResponse(json.dumps({
            'keywords': response,
            'metadata': {'model': MODEL, 'max_tokens': MAX_TOKENS, 'use_nmr': USE_NMR}
        }))
    else:
        return func.HttpResponse(
             'Please provide at least one of the following values in your request: title, description, body',
             status_code = 500
        )
