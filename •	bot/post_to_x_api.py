import os, tweepy

def _client_and_api():
    ck  = os.environ["TWITTER_API_KEY"]
    cs  = os.environ["TWITTER_API_SECRET"]
    at  = os.environ["TWITTER_ACCESS_TOKEN"]
    ats = os.environ["TWITTER_ACCESS_SECRET"]
    auth = tweepy.OAuth1UserHandler(ck, cs, at, ats)
    api  = tweepy.API(auth)  # v1.1 media
    client = tweepy.Client(consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)
    return client, api

def post_with_api(caption, image_path, alt_text=None):
    client, api = _client_and_api()
    media = api.media_upload(filename=image_path)
    if alt_text:
        try: api.create_media_metadata(media.media_id, alt_text=alt_text)
        except Exception: pass
    resp = client.create_tweet(text=caption, media_ids=[media.media_id_string])
    return str(resp.data["id"]) if resp and resp.data and "id" in resp.data else None

def fetch_public_metrics(tweet_id):
    client, _ = _client_and_api()
    tw = client.get_tweet(tweet_id, tweet_fields=["public_metrics","created_at"])
    return dict(tw.data.public_metrics) if tw and tw.data else {}
