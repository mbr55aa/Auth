from abc import ABC, abstractmethod


class OauthService(ABC):
    @abstractmethod
    def get_code(self, code: str):
        pass

    @abstractmethod
    def redirect_to_oauth(self):
        pass
