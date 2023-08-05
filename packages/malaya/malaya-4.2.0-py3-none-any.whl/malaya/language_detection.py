import pickle
from malaya.function import check_file
from malaya.model.ml import LanguageDetection
from malaya.model.tf import DeepLang
from malaya.path import PATH_LANG_DETECTION, S3_PATH_LANG_DETECTION
from herpetologist import check_type

lang_labels = {
    0: 'eng',
    1: 'ind',
    2: 'malay',
    3: 'manglish',
    4: 'other',
    5: 'rojak',
}

label = list(lang_labels.values())


@check_type
def fasttext(quantized: bool = True, **kwargs):

    """
    Load Fasttext language detection model.
    
    Parameters
    ----------
    quantized: bool, optional (default=True)
        if True, load quantized fasttext model. Else, load original fasttext model.

    Returns
    -------
    result : malaya.model.ml.LanguageDetection class
    """

    try:
        import fasttext
    except:
        raise ModuleNotFoundError(
            'fasttext not installed. Please install it by `pip install fasttext` and try again.'
        )
    if quantized:
        model = 'fasttext-quantized'
    else:
        model = 'fasttext-original'
    check_file(
        PATH_LANG_DETECTION[model], S3_PATH_LANG_DETECTION[model], **kwargs
    )

    try:
        model_fasttext = fasttext.load_model(
            PATH_LANG_DETECTION[model]['model']
        )
    except:
        raise ValueError(
            f"model corrupted due to some reasons, please run malaya.clear_cache('language-detection/{model}') and try again"
        )
    return LanguageDetection(model_fasttext, lang_labels)


def deep_model(**kwargs):
    """
    Load deep learning language detection model.

    Returns
    -------
    result : malaya.model.tf.DeepLang class
    """

    check_file(
        PATH_LANG_DETECTION['deep'], S3_PATH_LANG_DETECTION['deep'], **kwargs
    )
    try:
        with open(PATH_LANG_DETECTION['deep']['vector'], 'rb') as fopen:
            vector = pickle.load(fopen)
    except:
        raise ValueError(
            "model corrupted due to some reasons, please run malaya.clear_cache('language-detection/deep') and try again"
        )

    from malaya.text.bpe import load_yttm

    bpe, subword_mode = load_yttm(PATH_LANG_DETECTION['deep']['bpe'])

    import os

    return DeepLang(
        os.path.dirname(PATH_LANG_DETECTION['deep']['model']),
        vector,
        lang_labels,
        bpe,
        subword_mode,
    )
