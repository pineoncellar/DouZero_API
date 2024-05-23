port = 24813
timeout = 1800  # 超过此时长游戏未继续进行则删除游戏进程，单位s
###############################################################################################
version = 1.2
###############################################################################################
import os
import time
import json
import threading
from douzero.evaluation.simulation import init, next, env_list
from http.server import HTTPServer, BaseHTTPRequestHandler

lock = threading.Lock()

"""post data
{
    action: "", #init/play
    data: {}
    #(init:){
        "pid", # process_id
        "three_landlord_cards",
        "ai_amount": int,
        "player_data":[
            {
                "model", #WP/ADP/...
                "hand_cards",
                "position_code"
            },
            {
                "model", #WP/ADP/...
                "hand_cards",
                "position_code",
            }
        ]
    }
    (play:){
        "pid",
        "player",
        "cards"
    }
}
"""

"""response data
{
    type: "", # init/step
    action: "", # receive/play
    status: "", # ok/fail
    msg: "", # status为fail时不为空
    data: {} # status为fail时，如果能获取到pid则为{"pid"}，否则为{}
    #(receive:){
        "pid": str,
        "game_over": boolen
    }
    (play:){
        "pid": pid,
        "play": [
            {
                "cards": [],
                "confidence": ""
            },
            {
                "cards": [],
                "confidence": ""
            }
        ],
        "game_over": boolen
    }
}
"""


class Request(BaseHTTPRequestHandler):
    timeout = 3
    server_version = "Beta"

    def do_GET(self):
        self.send_response(200)
        self.send_header("type", "get")
        self.end_headers()

        res = json.dumps(
            {
                "info": "DouZero API",
                "version": version,
                "link": [
                    "https://github.com/kwai/DouZero",
                    "https://github.com/tianqiraf/DouZero_For_HappyDouDiZhu",
                ],
            }
        )
        res = str(res).encode()

        self.wfile.write(res)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["content-length"]))
        data = data.decode()
        data = json.loads(data)
        res = {}

        print(f"get post data: {data}\n")

        if data["action"] == "init":  # 初始化阶段
            print(f"get initialize request, initializing...")
            res = init(data["data"])

        elif data["action"] == "play":  # 出牌阶段
            res = next(data["data"])

        self.send_response(200)
        self.send_header("type", "post")
        self.end_headers()

        print(f"response:{res}\n")
        res = json.dumps(res)
        res = str(res).encode()
        self.wfile.write(res)


class TimeCheck(threading.Thread):
    def run(self):
        while True:
            global env_list
            with lock:
                timestamp = time.time()
                tmp_env_list = dict(env_list.items())
                for k, v in tmp_env_list.items():
                    existed_times = timestamp - v.timestamp
                    if existed_times > timeout:
                        del env_list[k]
                        print(f"pid:{k} game timeout, deleted.")
            time.sleep(300)


if __name__ == "__main__":
    print(f"DouZero_API . ver{version}")

    # 才疏学浅，不知道这两行的用途与意义，暂且保留
    os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    time_check = TimeCheck()
    time_check.start()

    host = ("127.0.0.1", port)
    print(f"listen at port {port}")
    server = HTTPServer(host, Request)
    server.serve_forever()  # 开启服务
