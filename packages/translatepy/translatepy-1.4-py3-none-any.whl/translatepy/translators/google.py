from typing import Union
from requests import get
from json import loads

from translatepy.utils.annotations import Tuple

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

class GoogleTranslate():
    """A Python implementation of Google Translate's APIs"""
    def __init__(self) -> None:
        pass

    def translate(self, text, destination_language, source_language="auto") -> Union[Tuple[str, str], Tuple[None, None]]:
        """
        Translates the given text to the given language

        Args:
          text: param destination_language:
          source_language: Default value = "auto")
          destination_language: 

        Returns:
            Tuple(str, str) --> tuple with source_lang, translation
            None, None --> when an error occurs

        """
        try:
            if source_language is None:
                source_language = "auto"
            request = get("https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&sl=" + str(source_language) + "&tl=" + str(destination_language) + "&q=" + str(text))
            if request.status_code < 400:
                data = loads(request.text)
                return data[2], "".join([sentence[0] for sentence in data[0]])
            else:
                request = get("https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=" + str(source_language) + "&tl=" + str(destination_language) + "&q=" + str(text), headers=HEADERS)
                if request.status_code < 400:
                    data = loads(request.text)
                    return data['ld_result']["srclangs"][0], "".join(sentence["trans"] for sentence in data["sentences"])
                else:
                    return None, None
        except:
            return None, None

    def transliterate():
        """Transliterates the given text"""
        raise NotImplementedError

    def define():
        """Returns the definition of the given word"""
        raise NotImplementedError

    def language(self, text) -> Union[str, None]:
        """
        Gives back the language of the given text

        Args:
          text: 

        Returns:
            str --> the language code
            None --> when an error occurs

        """
        try:
            request = get("https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&sl=auto&tl=ja&q=" + str(text))
            if request.status_code < 400:
                return loads(request.text)[2]
            else:
                request = get("https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=auto&tl=ja&q=" + str(text), headers=HEADERS)
                if request.status_code < 400:
                    return loads(request.text)['ld_result']["srclangs"][0]
                else:
                    return None
        except:
            return None

    def __repr__(self) -> str:
        return "Google Translate"
