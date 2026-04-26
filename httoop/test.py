class CLI:

    def __init__(self):
        self.modes = {
            'request': self.request,
            'response': self.response,
            'parse': {
                'request': self.parse_request,
                'response': self.parse_response,
            }
        }
