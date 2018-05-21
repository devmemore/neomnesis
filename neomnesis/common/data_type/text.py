class Text(str):

    def __new__(cls,text):
        return super().__new__(cls,text)
