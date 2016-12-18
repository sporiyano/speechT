# Copyright 2016 Louis Kirsch. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os
import tarfile
import urllib.request


class SpeechCorpusProvider:
  """
  Ensures the availability and downloads the speech corpus if necessary
  """

  TRAIN_DIR = 'train'
  DEV_DIR = 'dev'
  TEST_DIR = 'test'

  DEV_CLEAN_SET = 'dev-clean'
  TRAIN_CLEAN_100_SET = 'train-clean-100'
  TRAIN_CLEAN_360_SET = 'train-clean-360'
  TEST_CLEAN_SET = 'test-clean'
  DATA_SETS = {
    (DEV_DIR, DEV_CLEAN_SET),
    (TRAIN_DIR, TRAIN_CLEAN_100_SET),
    (TRAIN_DIR, TRAIN_CLEAN_360_SET),
    (TEST_DIR, TEST_CLEAN_SET)
  }

  BASE_URL = 'http://www.openslr.org/resources/12/'
  SET_FILE_EXTENSION = '.tar.gz'
  TAR_ROOT = 'LibriSpeech/'

  def __init__(self, data_directory):
    self._data_directory = data_directory
    self._make_dir_if_not_exists(data_directory)
    self._make_dir_if_not_exists(os.path.join(
      data_directory, SpeechCorpusProvider.DEV_DIR))
    self._make_dir_if_not_exists(os.path.join(
      data_directory, SpeechCorpusProvider.TRAIN_DIR))

  def _make_dir_if_not_exists(self, directory):
    if not os.path.exists(directory):
      os.makedirs(directory)

  def _download_if_not_exists(self, remote_file_name):
    path = os.path.join(self._data_directory, remote_file_name)
    if not os.path.exists(path):
      print('Downloading {}...'.format(remote_file_name))
      urllib.request.urlretrieve(SpeechCorpusProvider.BASE_URL + remote_file_name, path)
    return path

  @staticmethod
  def _extract_from_to(tar_file_name, source, target_directory):
    print('Extracting {}...'.format(tar_file_name))
    with tarfile.open(tar_file_name, 'r:gz') as tar:
      source_members = [
        tarinfo for tarinfo in tar.getmembers()
        if tarinfo.name.startswith(SpeechCorpusProvider.TAR_ROOT + source)
        ]
      for member in source_members:
        # Extract without prefix
        member.name = member.name.replace(SpeechCorpusProvider.TAR_ROOT, '')
      tar.extractall(target_directory, source_members)

  def _is_ready(self, data_sets=DATA_SETS):
    data_set_paths = [os.path.join(set_type, set_name)
                      for set_type, set_name in data_sets]
    return all([os.path.exists(os.path.join(
      self._data_directory, data_set
    )) for data_set in data_set_paths])

  def _download(self, data_sets=DATA_SETS):
    for data_set_type, data_set_name in data_sets:
      remote_file = data_set_name + SpeechCorpusProvider.SET_FILE_EXTENSION
      self._download_if_not_exists(remote_file)

  def _extract(self, data_sets=DATA_SETS):
    for data_set_type, data_set_name in data_sets:
      local_file = os.path.join(
        self._data_directory, data_set_name + SpeechCorpusProvider.SET_FILE_EXTENSION)
      target_directory = os.path.join(self._data_directory, data_set_type)
      self._extract_from_to(local_file, data_set_name, target_directory)
    pass

  def ensure_availability(self, test_only=False):
    if test_only:
      data_sets = [(SpeechCorpusProvider.TEST_DIR, SpeechCorpusProvider.TEST_CLEAN_SET)]
    else:
      data_sets = SpeechCorpusProvider.DATA_SETS

    if not self._is_ready(data_sets):
      self._download(data_sets)
      self._extract(data_sets)
