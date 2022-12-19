class Topic:
    def __init__(self, config, topic_name):
        print(self)
        if config.provider == 'Azure':
            self.client = ''
        else:
            print('Failed to initialize queue')
