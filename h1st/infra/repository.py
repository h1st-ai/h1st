from abc import ABC, abstractmethod


class IRepository(ABC):
    @abstractmethod
    def persist():
        raise NotImplementedError
    
    @abstractmethod
    def load():
        raise NotImplementedError
    

class LocalRepository(IRepository):
    def persist(self):
        print('Persist model to Local')

    def load(self):
        print('Load model from local')


class S3Repository(IRepository):
    def persist(self):
        print('Persist model to S3')

    def load(self):
        print('Load model from S3')


class RepositoryFactory:
    @classmethod
    def get_repo(self, config: str = None) -> IRepository:
        HANDLERS = {
            'local': LocalRepository,
            's3': S3Repository
        }
        handler = HANDLERS.get(config, LocalRepository)
        return handler()
