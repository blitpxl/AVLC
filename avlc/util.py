import os
import random


def get_local_file(file):
    return os.path.join(os.path.split(__file__)[0], file)


class RandomMediaIndexGenerator(object):
    def __init__(self):
        super(RandomMediaIndexGenerator, self).__init__()
        self.generatedIndex = []

    def __call__(self, media_count: int):
        randomIndex = random.randint(0, media_count - 1)
        while randomIndex in self.generatedIndex and len(self.generatedIndex) < media_count:
            randomIndex = random.randint(0, media_count - 1)
        self.generatedIndex.append(randomIndex)
        if len(self.generatedIndex) >= media_count:
            return None
        else:
            return randomIndex
