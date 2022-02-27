import __init__
from h1st.core.serdes import SerDes
from h1st.core.serializable import Serializable

class MySerializable(Serializable):
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        super().__init__()


if __name__ == "__main__":
    def one_loop():
        obj = MySerializable(5, 6)
        file_object = obj.to_file()
        copy = MySerializable.from_file(file_object)
        assert obj.x == copy.x
        assert obj.y == copy.y
    
    import timeit
    print(timeit.timeit(one_loop, number = 1000))
    #one_loop()