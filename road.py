

class Road():
    def __init__(self, name, description, start, end):
        self.name = name
        self.description = description
        self.start = start
        self.end = end

    def __str__(self):
        return self.name