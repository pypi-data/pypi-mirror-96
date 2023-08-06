# COPYRIGHT (C) 2020-2021 Nicotine+ Team
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import multiprocessing
import os
import pytest
import queue

from pynicotine.shares import Shares
from pynicotine.config import Config
from pynicotine.utils import apply_translation

DB_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dbs")
SHARES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sharedfiles")


@pytest.fixture(scope="module", autouse=True)
def setup():
    # Setting gettext and locale
    apply_translation()

    # Use 'spawn' start method for file scanning process
    multiprocessing.set_start_method("spawn")


def test_shares_scan():
    """ Test a full shares scan """

    config = Config("temp_config", DB_DIR)
    config.sections["transfers"]["shared"] = [("Shares", SHARES_DIR)]

    shares = Shares(None, config, queue.Queue(0))
    shares.rescan_public_shares(thread=False)

    # Verify that modification time was saved for shares folder
    assert SHARES_DIR in list(shares.share_dbs["mtimes"])

    # Verify that shared files were added
    assert ('dummy_file', 0, None, None) in shares.share_dbs["files"]["Shares"]
    assert ('nicotinetestdata.mp3', 80919, (128, 0), 5) in shares.share_dbs["files"]["Shares"]

    # Verify that expected folder is empty
    assert len(shares.share_dbs["files"]["Shares\\folder2"]) == 0

    # Verify that search index was updated
    word_index = shares.share_dbs["wordindex"]
    nicotinetestdata_indexes = list(word_index["nicotinetestdata"])
    ogg_indexes = list(word_index["ogg"])

    assert set(word_index) == set(
        ['nicotinetestdata', 'ogg', 'mp3', 'shares', 'file', 'dummy', 'folder1', 'folder2', 'nothing', 'something', 'test']
    )
    assert len(nicotinetestdata_indexes) == 2
    assert len(ogg_indexes) == 1

    # File ID associated with word "ogg" should return our nicotinetestdata.ogg file
    assert ogg_indexes[0] in nicotinetestdata_indexes
    assert shares.share_dbs["fileindex"][str(ogg_indexes[0])][0] == 'Shares\\nicotinetestdata.ogg'

    shares.close_shares("normal")


def test_hidden_file_folder_scan():
    """ Test that hidden files and folders are excluded """

    config = Config("temp_config", DB_DIR)
    config.sections["transfers"]["shared"] = [("Shares", SHARES_DIR)]

    shares = Shares(None, config, queue.Queue(0))
    shares.rescan_public_shares(thread=False)

    # Check folders
    mtimes = list(shares.share_dbs["mtimes"])

    assert os.path.join(SHARES_DIR, ".abc") not in mtimes
    assert os.path.join(SHARES_DIR, ".xyz") not in mtimes
    assert os.path.join(SHARES_DIR, "folder1") in mtimes
    assert os.path.join(SHARES_DIR, "folder2") in mtimes
    assert os.path.join(SHARES_DIR, "folder2", ".poof") not in mtimes
    assert os.path.join(SHARES_DIR, "folder2", "test") in mtimes
    assert os.path.join(SHARES_DIR, "something") in mtimes

    # Check files
    files = shares.share_dbs["files"]["Shares"]

    assert (".abc_file", 0, None, None) not in files
    assert (".hidden_file", 0, None, None) not in files
    assert (".xyz_file", 0, None, None) not in files
    assert ("dummy_file", 0, None, None) in files
    assert len(files) == 3

    shares.close_shares("normal")


def test_shares_add_downloaded():
    """ Test that downloaded files are added to shared files """

    config = Config("temp_config", DB_DIR)
    config.sections["transfers"]["shared"] = [("Downloaded", SHARES_DIR)]
    config.sections["transfers"]["sharedownloaddir"] = True

    shares = Shares(None, config, queue.Queue(0), None)
    shares.add_file_to_shared(os.path.join(SHARES_DIR, 'nicotinetestdata.mp3'))

    assert ('nicotinetestdata.mp3', 80919, (128, 0), 5) in shares.share_dbs["files"]["Downloaded"]
    assert ('Downloaded\\nicotinetestdata.mp3', 80919, (128, 0), 5) in shares.share_dbs["fileindex"].values()

    shares.close_shares("normal")
