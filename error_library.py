class Format_result:
    def __init__(self):
        self.response = []
        self.error = str


error501 = Format_result()
error501.error = 501
error501.response = ""
error501.can_connect = False

error502 = Format_result()
error502.error = 502
error502.response = ""
error502.can_connect = False