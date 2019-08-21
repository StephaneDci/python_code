# -*- coding: utf-8 -*-

"""
Classe  permettant de rajouter des méthodes au module SlackClient
Permet de simplifier l'envoi des messages Slack
Herite de la classe SlackClient
Les méthodes accèdent à api_call() de la classe Mère
Auteur : Stéphane Di Cioccio
 """

# Import de la classe SlackClient (mère)
from slackclient import SlackClient

# https://realpython.com/getting-started-with-the-slack-api-using-python-and-flask/
# get Token here : https://api.slack.com/custom-integrations/legacy-tokens

# Plusieurs Modules Python pour Slack :
# SlackClient : https://github.com/os/slacker   <= celui que nous utilisons
# Slacker : https://github.com/os/slacker


class Slack(SlackClient):

    # Le constructeur appelle simplement le constructeur de SlackClient avec le token
    def __init__(self, token):
        SlackClient.__init__(self, token)

    def slack_connection_test(self):
        print(self.api_call("api.test"))
        print(self.api_call("auth.test"))

    def list_channels(self):
        channels_call = self.api_call("channels.list")
        if channels_call.get('ok'):
            return channels_call['channels']
        return None

    def _get_channel_id(self, channel_name):
        channels_call = self.api_call("channels.list")
        if channels_call.get('ok'):
            for channel in channels_call['channels']:
                if channel['name'] == channel_name:
                    requested_id = channel['id']
                    print("OK FOUND ! Channel Name : {} <=> ID : {} ".format(channel_name, requested_id))
                    return requested_id
        else:
            print("Unable to authenticate...")

        print("NOT FOUND : channel: {}".format(channel_name))
        return None

    def _channel_info(self, channel_id):
        chan_info = self.api_call("channels.info", channel=channel_id)
        if chan_info:
            return chan_info['channel']
        return None

    def _send_message_on_channel_id(self, channel_id, message, nickname='Stephane(Python-bot)'):
        print("Sending Message on Channel {}".format(channel_id))
        self.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username=nickname,
            icon_emoji=':robot_face:')

    def send_message(self, channel_name, message, nick='Stephane(API)'):
        """
        Méthode publique pour envoyer des messsages sur un channel slack via son nom
        Attention il faut utiliser le Channel Name (visible dans Slack) et non le Channel ID
        """
        channel_id = self._get_channel_id(channel_name)
        self._send_message_on_channel_id(channel_id, message, nick)


if __name__ == '__main__':
    slack_token = 'xxxxxxxxxxx'
    slack_instance = Slack(slack_token)
    slack_instance.send_message('devapi', "Tests de l'API via classe Heritée")

"""
Utilisation comme module
# import Slack.Slackapi as Slack
# slack_token = 'xxxx'
# slack_instance = Slack.Slack(slack_token)
# slack_instance.send_message('devapi', "Tests de l'API via appel module")
"""
