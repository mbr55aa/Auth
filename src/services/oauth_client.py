class OauthClient:
    def __init__(
        self,
        social_name: str,
        app_id: str,
        app_redirect_url: str = None,
        permissions: dict = None,
        api_v: str = None,
        security_code: str = None,
        email: str = None,
        pswd: str = None,
    ):
        """
        Args:
            permissions: list of Strings with permissions to get from API
            app_id: (String) vk app id that one can get from vk.com
            api_v: (String) vk API version
        """

        self.user_id = None
        self.access_token = None
        self.first_name = None
        self.last_name = None
        self.bdate = None
        self.permissions = permissions
        self.api_v = api_v
        self.app_id = app_id
        self.security_code = security_code
        self.email = email
        self.pswd = pswd
        self.code = None
        self.expires_in = None
        self.login = None
        self.app_redirect_url = app_redirect_url
        self.social_name = social_name

    def __repr__(self):
        return f"""access_token: {self.access_token}, expires_in: {self.expires_in}, user_id: {self.user_id}, 
        email:{self.email}, bdate: {self.bdate}, last_name: {self.last_name}, first_name: {self.first_name},
        """
