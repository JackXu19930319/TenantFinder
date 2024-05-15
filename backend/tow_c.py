# https://github.com/2captcha/2captcha-python
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA', '')

solver = TwoCaptcha(api_key)


def get_tow_c():
    try:
        result = solver.normal('captcha.jpg')
    except Exception as e:
        sys.exit(e)
    else:
        code = result.get('code')
        os.remove('captcha.jpg')
        return code
