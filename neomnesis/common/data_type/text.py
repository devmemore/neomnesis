class Text(str):

    def __new__(cls,text):
        return super().__new__(cls,text)

    def to_str(self):
        return str(self)
