#!/usr/bin/python3

# In order for this script to run successfully, the operator needs to
# update the slackWebHook variable with their own webhook generated
# from slack. This can be generated by Creating a channel, an app and
# then enabling Incoming Webhooks within the Slack App. Once the 
# webhook is enabled, it will return a URL which needs to be added in
# the slackWebHook variable below

import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json
import threading
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

info = """
Brute Ratel C4 Notification Provider
Author : Paranoid Ninja
"""

usage = """
Usage : badgerNotifier.py slack <certfile> <keyfile>
Eg.   : badgerNotifier.py slack /etc/letsencrypt/live/evasionlabs.com/fullchain.pem /etc/letsencrypt/live/evasionlabs.com/privkey.pem
"""

LHOST = "0.0.0.0"
LPORT = 8080
slackWebHookUrl = "https://hooks.slack.com/services/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"

class NotificationHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        content = f"{message}"
        return content.encode("utf8")

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("404 Not Found"))
        currtime = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
        print("[" + currtime + "] GET request from " + self.address_string())
        for x, y in self.headers.items():
            print("  - ", x, ": ", y )
        print("------------------------------------------------------------")

    def do_HEAD(self):
        self._set_headers()
        self.wfile.write(self._html("404 Not Found"))
        currtime = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
        print("[" + currtime + "] HEAD request from " + self.address_string())
        for x, y in self.headers.items():
            print("  - ", x, ": ", y )
        print("------------------------------------------------------------")

    def do_POST(self):
        try:
            postData = ((self.rfile.read(int(self.headers['content-length']))).decode('utf-8')).rstrip('\r\n\r\n\0')
            jdata = json.loads(postData)
            # print(jdata)
            if "badger" in jdata:
                b_id = jdata["badger"]
                currtime = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
                print(f"[+] {currtime} " + b_id + " checked in")
                if "badger_config" in jdata:
                    b_uid = jdata["badger_config"]["b_uid"]
                    b_h_name = jdata["badger_config"]["b_h_name"]
                    b_p_name = jdata["badger_config"]["b_p_name"]
                    b_pid = jdata["badger_config"]["b_pid"]
                    b_winver = jdata["badger_config"]["b_wver"]
                    b_bld = jdata["badger_config"]["b_bld"]
                    finalMsg = "Badger *" + b_id + "* checked in as user *" + b_uid + "* from host *" + b_h_name + "* spawned under process *" + b_pid + "::" + b_p_name + "* on Windows " + b_winver + " Build " + b_bld
                    # print(finalMsg)
                    self._set_headers()
                    self.wfile.write(self._html(""))
                    try:
                        requests.post(slackWebHookUrl, json={'text':finalMsg}, verify=False, headers={'Content-type': 'application/json'})
                    except Exception as ex:
                        print("[!] Exception:", ex)

        except Exception as ex:
            print("[-] Exception:", ex)

    def log_message(self, format, *args):
        return

def main():
    print(info)
    if (len(sys.argv) < 3):
        print(usage)
        return
    currtime = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
    print(f"[+] {currtime} Starting Badger Notification Handler for %s => {LHOST}:{LPORT}" % sys.argv[1])
    server = HTTPServer((LHOST, LPORT), NotificationHandler)
    server.socket = ssl.wrap_socket(server.socket, certfile=sys.argv[2], keyfile=sys.argv[3], server_side=True)
    thread = threading.Thread(None, server.serve_forever)
    thread.daemon = True
    thread.start()
    thread.join()

if __name__ == "__main__":
    main()
