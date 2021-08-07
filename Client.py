class Client():
    def __init__(self,user_id,name,email,signup_date,tickers,notifications,notsent):
        self.name = name
        self.user_id = user_id
        self.email = email
        self.signup_date = signup_date
        self.tickers = tickers
        self.notifications = notifications
        self.notsent1 = notsent
        self.notsent2 = notsent
        