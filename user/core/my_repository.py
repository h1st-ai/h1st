import __init__
from h1st.core.repository import Repository
from h1st.core.serializable import Serializable

class MySerializable(Serializable):
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        super().__init__()


if __name__ == "__main__":
    def one_loop():
        repo = Repository.get_instance()
        obj = MySerializable(5, 6)
        version = repo.persist_object(obj)
        copy = repo.load_object(MySerializable, version)
        #print(obj)
        #print(copy)
        assert obj.x == copy.x
        assert obj.y == copy.y
    
    #import timeit
    #print(timeit.timeit(one_loop, number = 1000))
    one_loop()