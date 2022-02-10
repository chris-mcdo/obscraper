from unittest.mock import Mock, mock_open, patch

from obscraper import __main__


def test_main_returns_expected_result_for_urls():

    mock_writer = mock_open()
    with patch(
        "obscraper._scrape.get_posts_by_urls", Mock(return_value={"urls": "urls"})
    ) as mock_get_by_url:

        with patch("obscraper.__main__.open", mock_writer):
            try:
                __main__.main(["-u", "url1", "url2", "-o", "outfile.json"])
            except SystemExit as sysexit:
                assert sysexit.code == 0
                assert mock_get_by_url.call_count == 1
                mock_writer.assert_called_once_with(
                    file="outfile.json", mode="w", encoding="utf-8"
                )
                output_string = "".join(
                    [
                        call.args[0].strip()
                        for call in mock_writer().write.call_args_list
                    ]
                )
                assert output_string == '[{"url":"urls","post":"urls"}]'


def test_main_returns_expected_result_for_dates():
    dates = [
        "26th August 2015",
        "18th January 2019",
    ]
    mock_writer = mock_open()
    with patch(
        "obscraper._scrape.get_posts_by_edit_date",
        Mock(return_value={"dates": "dates"}),
    ) as mock_get_by_date:
        with patch("obscraper.__main__.open", mock_writer):
            try:
                __main__.main(["-d"] + dates + ["-o", "outfile.json"])
            except SystemExit as sysexit:
                assert sysexit.code == 0
                assert mock_get_by_date.call_count == 1
                mock_writer.assert_called_once_with(
                    file="outfile.json", mode="w", encoding="utf-8"
                )
                output_string = "".join(
                    [
                        call.args[0].strip()
                        for call in mock_writer().write.call_args_list
                    ]
                )
                assert output_string == '[{"url":"dates","post":"dates"}]'


def test_main_returns_expected_result_for_all():
    mock_writer = mock_open()
    with patch(
        "obscraper._scrape.get_all_posts", Mock(return_value={"all": "all"})
    ) as mock_get_all:
        with patch("obscraper.__main__.open", mock_writer):
            try:
                __main__.main(["-a", "-o", "outfile.json"])
            except SystemExit as sysexit:
                assert sysexit.code == 0
                assert mock_get_all.call_count == 1
                mock_writer.assert_called_once_with(
                    file="outfile.json", mode="w", encoding="utf-8"
                )
                output_string = "".join(
                    [
                        call.args[0].strip()
                        for call in mock_writer().write.call_args_list
                    ]
                )
                assert output_string == '[{"url":"all","post":"all"}]'
