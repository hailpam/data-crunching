import time
import os
import requests

class Timer:
    '''
        Define a basic timer util which computes the elapsed using different units
        of measure.
    '''
    def __init__(self, creation_time):
        self.creation_time = int(creation_time * 10**6)
    
    def elapsed_us(self):
        '''
            Return the elapsed time since creation in microseconds.
        '''
        return int(time.time() * 10**6) - self.creaton_time
    
    def elapsed_ms(self):
        '''
            Return the elapsed time since creation in milliseconds.
        '''
        return int(time.time() * 10**3) - int(self.creation_time/10**3)
    
    def elapsed_s(self):
        '''
            Return the elapsed time since creation in seconds.
        '''
        return int(time.time()) - int(self.creation_time/10**6)

def is_path_existent(path):
    '''
        Check whether a path is already existent.
    '''
    try:
        os.stat(path)
        return True
    except Exception as e:
        print('error: [%s] is not existent' % path)
        return False

def retryable_get(url, uri, method, key, params):
    '''
        Retries on network glitches. Instead of giving up and abandoning, it backs off to then retry
        in a number of seconds proportial to the number of attempts.
    '''
    errors = 0
    while True:
        try:
            res = requests.get('%s/%s/%s?ApiKey=%s&%s' % (url, uri, method, key, params))
            return res
        except Exception as e:
            errors += 1
            print('error: an exception was thrown: %s' % e)
            print('warning: backing off %d seconds prior to retry...' % errors)
            time.sleep(errors)

def name_to_camelcase(name):
    '''
        Try to standardize naming using a Camelcase notation, with the first character as upper case.
    '''
    transformed = []
    parts = name.split(' ')
    for part in parts:
        part = part.lower()
        if "'" in part:
            part = name_to_camelcase(part.replace("'", " "))
            part = part.replace(" ", "'")
        chars = list(part)
        if len(chars) > 0:
            chars[0] = chars[0].upper()
        transformed.append(''.join(chars))

    return ' '.join(transformed)
