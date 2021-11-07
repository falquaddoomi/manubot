import pytest

from manubot.cite.url import get_url_csl_item_zotero


@pytest.mark.xfail(
    reason="Fails due to ratelimiting https://github.com/zotero/translation-server/issues/133"
)
def test_get_url_csl_item_zotero_nyt():
    """
    This command creates two translation-server queries.
    The first query is equivalent to:
    ```
    curl --verbose \
      --header "Content-Type: text/plain" \
      --data 'https://nyti.ms/1NuB0WJ' \
      'https://translate.manubot.org/web'
    ```
    Can fail due to NYT ratelimiting, see
    https://github.com/zotero/translation-server/issues/133
    """
    url = "https://nyti.ms/1NuB0WJ"
    csl_item = get_url_csl_item_zotero(url)
    assert csl_item["title"].startswith(
        "Unraveling the Ties of Altitude, Oxygen and Lung Cancer"
    )
    assert csl_item["author"][0]["family"] == "Johnson"


def test_get_url_csl_item_zotero_manubot():
    """
    This command creates two translation-server queries. The first query is
    equivalent to:
    ```
    curl --verbose \
      --header "Content-Type: text/plain" \
      --data 'https://greenelab.github.io/meta-review/v/0770300e1d5490a1ae8ff3a85ddca2cdc4ae0613/' \
      'https://translate.manubot.org/web'
    ```
    """
    url = "https://greenelab.github.io/meta-review/v/0770300e1d5490a1ae8ff3a85ddca2cdc4ae0613/"
    csl_item = get_url_csl_item_zotero(url)
    assert csl_item["title"] == "Open collaborative writing with Manubot"
    assert csl_item["author"][1]["family"] == "Slochower"
    # Zotero CSL exporter returns mixed string/int date-parts
    # https://github.com/zotero/zotero/issues/1603
    assert [int(x) for x in csl_item["issued"]["date-parts"][0]] == [2018, 12, 18]


@pytest.mark.skip(
    reason="test intermittently fails as metadata varies between two states"
)
def test_get_url_csl_item_zotero_github():
    """
    This command creates two translation-server queries. The first query is
    equivalent to:
    ```
    curl --verbose \
      --header "Content-Type: text/plain" \
      --data 'https://github.com/pandas-dev/pandas/tree/d5e5bf761092c59eeb9b8750f05f2bc29fb45927' \
      'https://translate.manubot.org/web'
    ```

    Note: this test may have temporary failures, due to performance of
          translation-server. It seems that sometimes translation-server
          returns a different title for the same URL. A real mystery.

    See also:
        https://github.com/manubot/manubot/pull/139#discussion_r328703233

    Proposed action:
        Probably should inquire upstream or change the test.
    """
    url = "https://github.com/pandas-dev/pandas/tree/d5e5bf761092c59eeb9b8750f05f2bc29fb45927"
    csl_item = get_url_csl_item_zotero(url)
    # FIXME: arbitrarily, csl_item['abstract'], and not csl_item['title'] contains the title.
    assert csl_item["title"].startswith("Flexible and powerful data analysis")
    assert csl_item["source"] == "GitHub"


def test_get_url_csl_item_zotero_no_url(monkeypatch):
    """
    Ensure get_url_csl_item_zotero sets URL to the query URL,
    when the Zotero translator does not return it.
    https://github.com/manubot/manubot/issues/244
    """
    query_url = "http://icbo2016.cgrb.oregonstate.edu/node/251"

    def mock_web_query(url: str):
        assert url == query_url
        return [
            {
                "key": "J86G3MS7",
                "version": 0,
                "itemType": "webpage",
                "creators": [
                    {
                        "firstName": "Senay",
                        "lastName": "Kafkas",
                        "creatorType": "author",
                    },
                    {"firstName": "Ian", "lastName": "Dunham", "creatorType": "author"},
                    {
                        "firstName": "Helen",
                        "lastName": "Parkinson",
                        "creatorType": "author",
                    },
                    {
                        "firstName": "Johanna",
                        "lastName": "Mcentyre",
                        "creatorType": "author",
                    },
                ],
                "tags": [],
                "title": "BIT106: Use of text mining for Experimental Factor Ontology coverage expansion in the scope of target validation",
                "date": "2016",
                "shortTitle": "BIT106",
            }
        ]

    monkeypatch.setattr("manubot.cite.zotero.web_query", mock_web_query)
    csl_item = get_url_csl_item_zotero(query_url)
    assert "URL" in csl_item
    assert csl_item["URL"] == query_url
