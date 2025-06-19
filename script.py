import requests
from bs4 import BeautifulSoup, Comment
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import date
import html 

SLACK_TOKEN = "xoxb-9066268312470-9071244937893-jUxxcjxCie9GNuWrKr7niycs"
CHANNEL_ID = "C091PL1RW79" 

def crawl_and_parse():
    today = date.today().strftime("%Y-%m-%d")
    url = f"https://www.kaist.ac.kr/kr/html/campus/053001.html?dvs_cd=east1&stt_dt={today}"

    # Exception for breakfast.. i don't know how to handle it better than this 
    html_text = requests.get(url).text
    html_text = html_text.replace("<!-- <ul class=\"list-1st\"> -->", "<ul class=\"list-1st\">")
    html_text = html_text.replace("<!-- </ul> -->", "</ul>")

    soup = BeautifulSoup(html_text, "html.parser")
    
    table = soup.find("table", class_="table")
    headers = [th.text.strip() for th in table.find_all("th")]

    cells = table.find("tbody").find("tr").find_all("td")

    def parse_ul_from_td(td):
        ul = td.find("ul", class_="list-1st")
        if not ul:
            return []
        raw = ul.decode_contents().split("<br/>")
        return [
            html.unescape(line.strip())
            for line in raw if line.strip()
        ]

    menu = {
        headers[i]: parse_ul_from_td(cells[i])
        for i in range(len(headers))
    }

    msg = ""
    for time, items in menu.items():
        msg += f"\n[{time}]\n"
        for item in items:
            msg += f"- {item}\n"

    return msg

def post_to_slack(message):
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=CHANNEL_ID, text=message)
    except SlackApiError as e:
        print(f"Slack Error: {e.response['error']}")

if __name__ == "__main__":
    msg = crawl_and_parse()
    post_to_slack(msg)
