# This file is part of pyacoustid.
# Copyright 2014, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

import contextlib
import errno
import json
import os

import requests

try:
    import audioread

    have_audioread = True
except ImportError:
    have_audioread = False
try:
    import chromaprint

    have_chromaprint = True
except ImportError:
    have_chromaprint = False
import gzip
import subprocess
import threading
import time
from io import BytesIO

API_BASE_URL = "http://api.acoustid.org/v2/"
DEFAULT_META = ["recordings"]
REQUEST_INTERVAL = 0.33  # 3 requests/second.
MAX_AUDIO_LENGTH = 120  # Seconds.
FPCALC_COMMAND = "fpcalc"
FPCALC_ENVVAR = "FPCALC"
MAX_BIT_ERROR = 2  # comparison settings
MAX_ALIGN_OFFSET = 120


# Exceptions.


class AcoustidError(Exception):
    """Base for exceptions in this module."""


class FingerprintGenerationError(AcoustidError):
    """The audio could not be fingerprinted."""


class NoBackendError(FingerprintGenerationError):
    """The audio could not be fingerprinted because neither the
    Chromaprint library nor the fpcalc command-line tool is installed.
    """


class FingerprintSubmissionError(AcoustidError):
    """Missing required data for a fingerprint submission."""


class WebServiceError(AcoustidError):
    """The Web service request failed. The field ``message`` contains a
    description of the error. If this is an error that was specifically
    sent by the acoustid server, then the ``code`` field contains the
    acoustid error code.
    """

    def __init__(self, message, response=None):
        """Create an error for the given HTTP response body, if
        provided, with the ``message`` as a fallback.
        """
        if response:
            # Try to parse the JSON error response.
            try:
                data = json.loads(response)
            except ValueError:
                pass
            else:
                if isinstance(data.get("error"), dict):
                    error = data["error"]
                    if "message" in error:
                        message = error["message"]
                    if "code" in error:
                        self.code = error["code"]

        super().__init__(message)
        self.message = message


# Endpoint configuration.


def set_base_url(url):
    """Set the URL of the API server to query."""
    pass


def _get_lookup_url():
    """Get the URL of the lookup API endpoint."""
    pass


def _get_submit_url():
    """Get the URL of the submission API endpoint."""
    pass


def _get_submission_status_url():
    """Get the URL of the submission status API endpoint."""
    pass


# Compressed HTTP request bodies.


def _compress(data):
    """Compress a bytestring to a gzip archive."""
    pass


class CompressedHTTPAdapter(requests.adapters.HTTPAdapter):
    """An `HTTPAdapter` that compresses request bodies with gzip. The
    Content-Encoding header is set accordingly.
    """

    def add_headers(self, request, **kwargs):
        pass


# Utilities.


class _rate_limit:  # noqa: N801
    """A decorator that limits the rate at which the function may be
    called.  The rate is controlled by the REQUEST_INTERVAL module-level
    constant; set the value to zero to disable rate limiting. The
    limiting is thread-safe; only one thread may be in the function at a
    time (acts like a monitor in this sense).
    """

    def __init__(self, fun):
        self.fun = fun
        self.last_call = 0.0
        self.lock = threading.Lock()

    def __call__(self, *args, **kwargs):
        with self.lock:
            # Wait until request_rate time has passed since last_call,
            # then update last_call.
            since_last_call = time.time() - self.last_call
            if since_last_call < REQUEST_INTERVAL:
                time.sleep(REQUEST_INTERVAL - since_last_call)
            self.last_call = time.time()

            # Call the original function.
            return self.fun(*args, **kwargs)


@_rate_limit
def _api_request(url, params, timeout=None):
    """Makes a POST request for the URL with the given form parameters,
    which are encoded as compressed form data, and returns a parsed JSON
    response. May raise a WebServiceError if the request fails.
    If the specified timeout passes, then raises a TimeoutError.
    """
    pass


# Main API.


def fingerprint(samplerate, channels, pcmiter, maxlength=MAX_AUDIO_LENGTH):
    """Fingerprint audio data given its sample rate and number of
    channels.  pcmiter should be an iterable containing blocks of PCM
    data as byte strings. Raises a FingerprintGenerationError if
    anything goes wrong.
    """
    pass


def lookup(apikey, fingerprint, duration, meta=DEFAULT_META, timeout=None):
    """Look up a fingerprint with the Acoustid Web service. Returns the
    Python object reflecting the response JSON data. To get more data
    back, ``meta`` can be a list of keywords from this list: recordings,
    recordingids, releases, releaseids, releasegroups, releasegroupids,
    tracks, compress, usermeta, sources.
    """
    pass


def parse_lookup_result(data):
    """Given a parsed JSON response, generate tuples containing the match
    score, the MusicBrainz recording ID, the title of the recording, and
    the artist name of the recording. Multiple artist names are joined
    by join phrases as displayed on web page. If an artist is not available,
    the last item is None. If the response is incomplete, raises a
    WebServiceError.
    """
    pass


def _fingerprint_file_audioread(path, maxlength):
    """Fingerprint a file by using audioread and chromaprint."""
    pass


def _fingerprint_file_fpcalc(path, maxlength):
    """Fingerprint a file by calling the fpcalc application."""
    pass


def fingerprint_file(path, maxlength=MAX_AUDIO_LENGTH, force_fpcalc=False):
    """Fingerprint a file either using the Chromaprint dynamic library
    or the fpcalc command-line tool, whichever is available (unless
    ``force_fpcalc`` is specified). Returns the duration and the
    fingerprint.
    """
    pass


def _popcount(x) -> int:
    """count 1s in binary encoding of x"""
    pass


def _match_fingerprints(a: list[int], b: list[int]) -> float:
    """Compare two Chromaprint fingerprints, given as numbers.

    For more details, see:
    https://essentia.upf.edu/tutorial_fingerprinting_chromaprint.html

    :param a: decompressed fingerprint
    :param b: decompressed fingerprint
    :return:  similarity score [0,1]
    """
    pass


def compare_fingerprints(a, b) -> float:
    """Compare two fingerprints produced by `fingerprint_file`.

    :param a: A pair produced by `fingerprint_file`.
    :param b: A second such pair.
    :return:  similarity score [0,1]
    """
    pass


def match(
    apikey, path, meta=DEFAULT_META, parse=True, force_fpcalc=False, timeout=None
):
    """Look up the metadata for an audio file. If ``parse`` is true,
    then ``parse_lookup_result`` is used to return an iterator over
    small tuple of relevant information; otherwise, the full parsed JSON
    response is returned. Fingerprinting uses either the Chromaprint
    library or the fpcalc command-line tool; if ``force_fpcalc`` is
    true, only the latter will be used. To get more data back, ``meta``
    can be a list of keywords from this list: recordings, recordingids,
    releases, releaseids, releasegroups, releasegroupids, tracks,
    compress, usermeta, sources.
    """
    pass


def submit(apikey, userkey, data, timeout=None):
    """Submit a fingerprint to the acoustid server. The ``apikey`` and
    ``userkey`` parameters are API keys for the application and the
    submitting user, respectively.

    ``data`` may be either a single dictionary or a list of
    dictionaries. In either case, each dictionary must contain a
    ``fingerprint`` key and a ``duration`` key and may include the
    following: ``puid``, ``mbid``, ``track``, ``artist``, ``album``,
    ``albumartist``, ``year``, ``trackno``, ``discno``, ``fileformat``,
    ``bitrate``

    If the required keys are not present in a dictionary, a
    FingerprintSubmissionError is raised.

    Returns the parsed JSON response.
    """
    pass


def get_submission_status(apikey, submission_id, timeout=None):
    """Get the status of a submission to the acoustid server.
    ``submission_id`` is the id of a fingerprint submission, as returned
    in the response object of a call to the ``submit`` endpoint.
    """
    pass
