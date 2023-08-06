"""Runner to process task to search tweets."""

from typing import List, Optional

from .parse import BaseTweetParser
from .parse import TweetParser
from .request_details_builder import get_search_tweet_request_details
from .search_run_context import SearchRunContext
from .search_tweets_result import SearchTweetsResult
from .search_tweets_task import SearchTweetsTask
from ..auth import AuthTokenProviderFactory, SimpleAuthTokenProviderFactory
from ..exceptions.scrap_batch_bad_response import ScrapBatchBadResponse
from ..http_request.request_details import RequestDetails
from ..http_request.web_client import WebClient
from stweet.http_request.requests.requests_web_client import RequestsWebClient
from ..model.tweet import Tweet
from ..tweet_output.tweet_output import TweetOutput


class TweetSearchRunner:
    """Runner class to process task to search tweets."""

    search_run_context: SearchRunContext
    search_tweets_task: SearchTweetsTask
    tweet_outputs: List[TweetOutput]
    web_client: WebClient
    tweet_parser: TweetParser
    auth_token_provider_factory: AuthTokenProviderFactory

    def __init__(
            self,
            search_tweets_task: SearchTweetsTask,
            tweet_outputs: List[TweetOutput],
            search_run_context: Optional[SearchRunContext] = None,
            web_client: WebClient = RequestsWebClient(),
            tweet_parser: TweetParser = BaseTweetParser(),
            auth_token_provider_factory: AuthTokenProviderFactory = SimpleAuthTokenProviderFactory()
    ):
        """Constructor to create object."""
        self.search_run_context = SearchRunContext() if search_run_context is None else search_run_context
        self.search_tweets_task = search_tweets_task
        self.tweet_outputs = tweet_outputs
        self.web_client = web_client
        self.tweet_parser = tweet_parser
        self.auth_token_provider_factory = auth_token_provider_factory
        return

    def run(self) -> SearchTweetsResult:
        """Main search_runner method."""
        self._prepare_token()
        while not self._is_end_of_scrapping():
            self._execute_next_tweets_request()
        return SearchTweetsResult(self.search_run_context.all_download_tweets_count)

    def _is_end_of_scrapping(self) -> bool:
        ctx = self.search_run_context
        return \
            ctx.last_tweets_download_count == 0 \
            or (ctx.scroll_token is None) \
            or self.search_run_context.all_download_tweets_count == self.search_tweets_task.tweets_limit

    def _execute_next_tweets_request(self):
        request_params = self._get_next_request_details()
        response = self.web_client.run_request(request_params)
        if response.is_token_expired():
            self._refresh_token()
        elif response.is_success():
            parsed_tweets = self.tweet_parser.parse_tweets(response.text)
            self.search_run_context.scroll_token = self.tweet_parser.parse_cursor(response.text)
            self._process_new_scrapped_tweets(parsed_tweets)
        else:
            raise ScrapBatchBadResponse(response)
        return

    def _process_new_scrapped_tweets(self, parsed_tweets: List[Tweet]):
        self._process_new_tweets_to_output(parsed_tweets)
        self.search_run_context.last_tweets_download_count = len(parsed_tweets)
        self.search_run_context.add_downloaded_tweets_count(len(parsed_tweets))

    def _get_next_request_details(self) -> RequestDetails:
        return get_search_tweet_request_details(self.search_run_context, self.search_tweets_task)

    def _refresh_token(self):
        token_provider = self.auth_token_provider_factory.create(self.web_client)
        self.search_run_context.guest_auth_token = token_provider.get_new_token()
        return

    def _prepare_token(self):
        if self.search_run_context.guest_auth_token is None:
            self._refresh_token()
        return

    def _process_new_tweets_to_output(self, new_tweets: List[Tweet]):
        for tweet_output in self.tweet_outputs:
            tweet_output.export_tweets(new_tweets)
        return
