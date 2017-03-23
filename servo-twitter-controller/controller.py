from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob
from serial import Serial

import json

from credentials import consumer_key, consumer_secret, access_token, access_token_secret

DEVICE = '/dev/cu.usbmodem1411'
serial = Serial(DEVICE, 9600)

sentiment_buffer = []
BUFF_SIZE = 5

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        global sentiment_buffer

        json_data = json.loads(data)
        text = json_data.get('text')

        if text is not None:
            blob = TextBlob(text)
            print(blob)
            print(blob.sentiment.polarity)
            print()

            sentiment_buffer.append(blob.sentiment.polarity)

            buffer_size = len(sentiment_buffer)

            if buffer_size > BUFF_SIZE:
                sentiment_buffer = sentiment_buffer[BUFF_SIZE - buffer_size:]

            avg_sentiment = sum(sentiment_buffer)/float(len(sentiment_buffer))

            # normalise it to be between 0 and 1
            avg_sentiment += 1
            avg_sentiment /= 2.0

            # just in case
            if avg_sentiment > 1:
                avg_sentiment = 1
            elif avg_sentiment < 0:
                avg_sentiment = 0

            print('Meter at', avg_sentiment)
            print()

            command = 'servo %.2f\n' % avg_sentiment
            serial.write(bytes(command, 'utf-8'))

        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['trump'])
