#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple server which adds a DocumentWordsProvider to the
CodeCompletion worker.

On Windows, this script is frozen by freeze_setup.py (cx_Freeze).
"""
from pyqode.core import backend

if __name__ == '__main__':
    backend.CodeCompletionWorker.providers.append(
        backend.DocumentWordsProvider())
    backend.serve_forever()
