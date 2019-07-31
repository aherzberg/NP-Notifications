import requests
from pprint import pprint
import json
import pickle
import np_util
import sched, time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = {
    "GAME_NUMBER": "",
    "API_CODE": "",
    "FROM_EMAIL_USERNAME": "",
    "FROM_MAIL_PASSWORD": "",
    "REFRESH_TIME_MINUTES": "",
    "TO_EMAIL_ADDRESS": "",
    "PLAYERS_TO_IGNORE": []
}

# tracks carriers previously notified as well as the html email text used for that carrier.
tracked_carriers = {}

def main():

    parse_config()

    game_data = api_call(config["GAME_NUMBER"], config["API_CODE"], False)

    parse_data(game_data)

    your_Id = game_data['scanning_data']['player_uid']

    time_looper(your_Id)


def parse_config():
    with open('config.txt', 'rt') as configFile:  # Open file lorem.txt for reading text
        for currentLine in configFile:  # For each line, read it to a string
            currentLine = currentLine.strip()
            # If string is not empty
            if currentLine:
                # if line is NOT a comment
                if currentLine[0] != "#":
                    if currentLine.split(":")[0] not in config:
                        print("ERROR: LINE '"+ currentLine + "' is not a valid config value")
                    else:
                        # put config value in config dictionary
                        if currentLine.split(":")[0] == "PLAYERS_TO_IGNORE":
                            config[currentLine.split(":")[0]] = currentLine.split(":")[1].split(";")
                        else:
                            config[currentLine.split(":")[0]] = currentLine.split(":")[1]

    print(config)


def time_looper(player_id):
    s = sched.scheduler(time.time, time.sleep)

    def update(sc):
        print("-------------UPDATE-------------")
        pprint(tracked_carriers)
        h = check_new_hostile_incoming_carriers(player_id)
        #pprint(h)
        email_text = "The following hostile carriers are incoming:<br/><br/>"
        for star_id in h.keys():
            star_obj = np_util.star_id_to_object(int(star_id))

            email_text += "<b>" + star_obj.name + "</b> (str: " + str(star_obj.strength) + ") is being attacked by "
            total_carrier_str = -1
            for carrier in h[star_id]:
                carrier_obj = np_util.carrier_id_to_object(carrier)
                email_text += "<b>"+np_util.player_id_to_obj(carrier_obj.owner).name+"</b> (color: "+np_util.id_to_color[carrier_obj.owner] + ", str: "+str(carrier_obj.strength)+"), "
                total_carrier_str += carrier_obj.strength

            combat_outcome = np_util.combat_calculate(star_obj.strength, np_util.player_id_to_obj(star_obj.owner).weapon_resh, total_carrier_str,np_util.player_id_to_obj(carrier_obj.owner).weapon_resh)
            if combat_outcome == "Defenders":
                text_outcome = "WIN"

            else:
                text_outcome = "LOSE"

            email_text += "<br>You will <b>" + text_outcome + "</b> this battle."
            # Remove last comma
            email_text = email_text[:-1:]
            email_text += "<br/><br/>"

            tracked_carriers[str(carrier_obj.id)+"-"+str(star_id)] = email_text
        email_text += "Respond at: <a href='https://np.ironhelmet.com/game/"+str(config["GAME_NUMBER"])+"'>https://np.ironhelmet.com/game/" + str(config["GAME_NUMBER"]) + "</a>"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Neptunes Pride - Your Under Attack!"
        msg['From'] = config["FROM_EMAIL_USERNAME"]
        msg['To'] = "aherzberg@gmail.com"
        html = "<html><head></head><body>"+email_text+"</body></html>"
        part1 = MIMEText(html, 'html')
        msg.attach(part1)
        email_server = configure_email()

        email_server.sendmail(config["FROM_EMAIL_USERNAME"], ['aherzberg5@gmail.com'], msg.as_string())
        email_server.close()

        s.enter(int(config["REFRESH_TIME_MINUTES"]) * 60, 1, update, (sc,))

    s.enter(1, 1, update, (s,))
    s.run()


def check_new_hostile_incoming_carriers(player_id):
    hostile_carriers_incoming = {}
    # loop through all of players stars
    for star in np_util.get_player_stars(player_id):
        #print(star.name)
        # see if any hostile carriers are incoming to star
        hc = np_util.hostile_carriers_incoming_to_star(star.id, player_id, config["PLAYERS_TO_IGNORE"])
        if len(hc) > 0:
            # add to dictionary with key as star id and values as carrier ids
            new_hc = []
            for carrier in hc:
                pprint(str(carrier)+"-"+str(star.id))
                if str(carrier)+"-"+str(star.id) not in tracked_carriers:
                    new_hc.append(carrier)
            hostile_carriers_incoming[str(star.id)] = new_hc

    return hostile_carriers_incoming


def configure_email():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        server.login(config["FROM_EMAIL_USERNAME"], config["FROM_MAIL_PASSWORD"])
        return server

    except:
        print('Something went wrong with email configuration...')


def parse_data(game_data):

    # parse star data into class objects
    for star in game_data['scanning_data']['stars'].keys():
        star_data = game_data['scanning_data']['stars'][star]
        np_util.Star(star_data['uid'],star_data['n'],star_data['st'] if 'st' in star_data else 0,star_data['puid'])

    # parse carrier data into class objects
    for carrier in game_data['scanning_data']['fleets'].keys():
        carrier_data = game_data['scanning_data']['fleets'][carrier]
        #pprint(carrier_data)
        waypoints = []
        for waypoint in carrier_data['o']:
            waypoints.append(np_util.star_id_to_object(waypoint[1]))

        np_util.Carrier(carrier_data['uid'],
                                    carrier_data['n'],
                                    carrier_data['st'],
                                    (carrier_data['x'], carrier_data['y']),
                                    waypoints,
                                    carrier_data['puid'])

    for player in game_data['scanning_data']['players'].keys():
        player_data = game_data['scanning_data']['players'][str(player)]
        #pprint(game_data['scanning_data'])
        np_util.Player(player, player_data['alias'], player_data['tech']['weapons']['level'])


def api_call(game_number, api_code, live_data):

    # non-live data should be used when testing to prevent spamming servers
    if live_data:

        data = {
            "api_version": "0.1",
            "game_number": game_number,
            "code": api_code,
        }
        r = requests.post('https://np.ironhelmet.com/api', data=data)
        print(r.status_code)
        print(r.headers)
        print(r.encoding)
        game_data = json.loads(r.text)

        # dump data into local storage for offline access to avoid spamming servers
        with open('objs.pkl', 'wb') as f:
            pickle.dump(json.loads(r.text), f)
    else:

        # load data from local storage.
        with open('objs.pkl', 'rb') as f:
            game_data = pickle.load(f)

    return game_data


if __name__ == '__main__':
    main()
