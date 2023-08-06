"""Utils to parse data from web response."""

import json
from datetime import datetime
from typing import List, Optional, Dict

from arrow import Arrow
from dateutil import parser

from .tweet_parser import TweetParser
from ...model import Tweet
from ...model.media import Media

_Tweet_formats = {
    'datetime': '%Y-%m-%d %H:%M:%S %Z',
    'datestamp': '%Y-%m-%d',
    'timestamp': '%H:%M:%S'
}


def _default_string_value(string: Optional[str], default_value: str) -> str:
    return string if string is not None else default_value


def _starts_with_any_of(text: str, start_value: List[str]) -> bool:
    for it in start_value:
        if text.startswith(it):
            return True
    else:
        return False


def _timeline_entry_content_contains_tweet(entry: any) -> bool:
    return 'tweet' in entry['content']['item']['content']


class BaseTweetParser(TweetParser):
    """Utils class to parse data from web response."""

    def parse_tweets(self, response_text: str) -> List[Tweet]:
        """Method to extract tweets from web response."""
        # main method part from twint -- https://github.com/twintproject/twint
        response_json = json.loads(response_text)
        if len(response_json['globalObjects']['tweets']) == 0:
            return []
        feed = []
        for timeline_entry in response_json['timeline']['instructions'][0]['addEntries']['entries']:
            # this will handle the cases when the timeline entry is a tweet
            if _starts_with_any_of(timeline_entry['entryId'], ['sq-I-t-', 'tweet-']):
                if _timeline_entry_content_contains_tweet(timeline_entry):
                    _id = timeline_entry['content']['item']['content']['tweet']['id']
                    # skip the ads
                    if 'promotedMetadata' in timeline_entry['content']['item']['content']['tweet']:
                        continue
                elif 'tombstone' in timeline_entry['content']['item']['content'] and 'tweet' in \
                        timeline_entry['content']['item']['content']['tombstone']:
                    _id = timeline_entry['content']['item']['content']['tombstone']['tweet']['id']
                else:
                    _id = None
                if _id is None:
                    raise ValueError('Unable to find ID of tweet in timeline.')
                try:
                    temp_obj = response_json['globalObjects']['tweets'][_id]
                except KeyError:
                    print('encountered a deleted tweet with id {}'.format(_id))
                    continue
                temp_obj['user_data'] = response_json['globalObjects']['users'][temp_obj['user_id_str']]
                if 'retweeted_status_id_str' in temp_obj:
                    rt_id = temp_obj['retweeted_status_id_str']
                    _dt = response_json['globalObjects']['tweets'][rt_id]['created_at']
                    _dt = datetime.strptime(_dt, '%a %b %d %H:%M:%S %z %Y')
                    _dt = response_json(_dt)
                    _dt = str(_dt.strftime(_Tweet_formats['datetime']))
                    temp_obj['retweet_data'] = {
                        'user_rt_id': response_json['globalObjects']['tweets'][rt_id]['user_id_str'],
                        'user_rt': response_json['globalObjects']['tweets'][rt_id]['full_text'],
                        'retweet_id': rt_id,
                        'retweet_date': _dt,
                    }
                feed.append(BaseTweetParser._tweet_dict_to_tweet_object(temp_obj))
        return feed

    @staticmethod
    def _tweet_dict_to_tweet_object(tweet) -> Tweet:
        return Tweet(
            created_at=Arrow.fromdatetime(parser.parse(tweet['created_at'])),
            id_str=tweet['id_str'],
            conversation_id_str=tweet['conversation_id_str'],
            # there was the problem with pandas exporting because \r is old version of \n
            full_text=tweet['full_text'].replace('\r', '\n'),
            lang=tweet['lang'],
            favorited=tweet['favorited'],
            retweeted=tweet['retweeted'],
            retweet_count=tweet['retweet_count'],
            favorite_count=tweet['favorite_count'],
            reply_count=tweet['reply_count'],
            quote_count=tweet['quote_count'],
            quoted_status_id_str=BaseTweetParser._get_default_string_value_from_dict(
                tweet, 'quoted_status_id_str'),
            quoted_status_short_url=BaseTweetParser._get_default_string_value_from_dict(
                tweet, 'quoted_status_short_url'),
            quoted_status_expand_url=BaseTweetParser._get_default_string_value_from_dict(
                tweet, 'quoted_status_expand_url'),
            user_id_str=tweet['user_data']['id_str'],
            user_name=tweet['user_data']['screen_name'],
            user_full_name=tweet['user_data']['name'],
            user_verified=tweet['user_data']['verified'],
            in_reply_to_status_id_str=_default_string_value(tweet['in_reply_to_status_id_str'], ''),
            in_reply_to_user_id_str=_default_string_value(
                tweet['in_reply_to_user_id_str'], ''),
            media=BaseTweetParser._get_media_list_from_tweet_object(tweet),
            hashtags=['#' + it['text'] for it in tweet['entities']['hashtags']],
            mentions=[it['screen_name'] for it in tweet['entities']['user_mentions']],
            urls=[it['url'] for it in tweet['entities']['urls']]
        )

    @staticmethod
    def _get_media_list_from_tweet_object(tweet: Dict[str, any]) -> List[Media]:
        if 'media' in tweet['entities']:
            return [Media(it['media_url_https'], it['type']) for it in tweet['entities']['media']]
        else:
            return []

    @staticmethod
    def _get_default_string_value_from_dict(tweet_dict: Dict[str, any], field: str, default_value: str = ''):
        return default_value if field not in tweet_dict else tweet_dict[field]

    @staticmethod
    def _parse_cursor_first_location(response_json: any) -> Optional[str]:
        try:
            return response_json['timeline']['instructions'][0]['addEntries']['entries'][-1]['content'][
                'operation']['cursor']['value']
        except KeyError:
            return None
        except IndexError:
            return None

    @staticmethod
    def _parse_cursor_second_location(response_json: any) -> Optional[str]:
        try:
            return response_json['timeline']['instructions'][-1]['replaceEntry']['entry']['content']['operation'][
                'cursor']['value']
        except KeyError:
            return None
        except IndexError:
            return None

    def parse_cursor(self, response_content: str) -> Optional[str]:
        """Method to extract next cursor to scrap request from web response."""
        response_json = json.loads(response_content)
        next_cursor = BaseTweetParser._parse_cursor_first_location(response_json)
        if next_cursor is None:
            next_cursor = BaseTweetParser._parse_cursor_second_location(response_json)
        return next_cursor
