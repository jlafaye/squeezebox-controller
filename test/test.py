
from squeezebox_controller import SqueezeBoxController, UserException
import requests
import requests.cookies
from unittest.mock import MagicMock, Mock
import json as json_lib

ip = "192.168.0.1"
url = "http://" + ip + ":9000/jsonrpc.js"

players = [{"name": "a", "playerid": "1"}, {"name": "b", "playerid": "2"}]

req_lookup_table = {
  '["", ["serverstatus", 0, 999]]': '{"result": {"player count": 2, "players_loop": ' + json_lib.dumps(players) +' }}'
}

def get_req_json(params):
  return {"method": "slim.request", "params": params}

def handle(*args, **kargs):
  assert len(args) == 1
  assert args[0] == url
  assert "json" in kargs
  json = kargs["json"]
  assert "method" in json
  assert json["method"] == "slim.request"
  assert "params" in json
  params = json["params"]
  assert len(params) == 2
  player = params[0]
  command = params[1]
  s = json_lib.dumps(params)
  print(s)
  if s in req_lookup_table:
    ret_val = req_lookup_table[s]
  else:
    ret_val = '{"result": "success"}'
  ret = Mock()
  ret.content = ret_val.encode("utf-8")
  return ret

requests_lib = Mock(spec=requests)
cookies = requests_lib.cookies.RequestsCookieJar()
requests_lib.post = Mock(side_effect=handle)

sbc = SqueezeBoxController(ip, request_lib=requests_lib)

requests_lib.post.reset_mock()
sbc.simple_command({"player": players[0]["name"], "command": "PLAY"})
requests_lib.post.assert_called_once_with(url, cookies=cookies, json=get_req_json([players[0]["playerid"], ["play"]]))


