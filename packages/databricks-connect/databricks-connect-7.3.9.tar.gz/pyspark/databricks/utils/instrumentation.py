#
# DATABRICKS CONFIDENTIAL & PROPRIETARY
# __________________
#
# Copyright 2020 Databricks, Inc.
# All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains the property of Databricks, Inc.
# and its suppliers, if any.  The intellectual and technical concepts contained herein are
# proprietary to Databricks, Inc. and its suppliers and may be covered by U.S. and foreign Patents,
# patents in process, and are protected by trade secret and/or copyright law. Dissemination, use,
# or reproduction of this information is strictly forbidden unless prior written permission is
# obtained from Databricks, Inc.
#
# If you view or obtain a copy of this information and believe Databricks, Inc. may not have
# intended it to be made available, please promptly report it to Databricks Legal Department
# @ legal@databricks.com.
#

import functools
import sys
import time
import traceback
from pyspark import SparkContext


def instrumented(func):
    """
    Instrument the function duration. If failed, it will also log error type and traceback.
    It won't log message in exception due to data privacy.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            logger = SparkContext._jvm.com.databricks.spark.util.PythonUsageLoggingImpl()
        except:
            # If creating logger failed, directly call func and return.
            return func(self, *args, **kwargs)

        try:
            start_time = time.time()
            return_val = func(self, *args, **kwargs)
        except Exception:
            duration = (time.time() - start_time) * 1000
            try:
                # log failure
                etype, _, tb = sys.exc_info()
                err_msg = "Traceback: \n" + ''.join(traceback.format_tb(tb))
                logger.recordFunctionDuration(
                    duration,
                    {
                        logger.tagDefinitions().TAG_CLASS_NAME(): self.__class__.__name__,
                        logger.tagDefinitions().TAG_FUNCTION_NAME(): func.__name__,
                        logger.tagDefinitions().TAG_STATUS(): 'failed',
                        logger.tagDefinitions().TAG_ERROR(): etype.__name__,
                        logger.tagDefinitions().TAG_ERROR_MESSAGE(): err_msg
                    },
                    ''
                )
            except:
                # swallow exceptions for safety
                pass
            raise
        else:
            duration = (time.time() - start_time) * 1000
            try:
                # log success
                logger.recordFunctionDuration(
                    duration,
                    {
                        logger.tagDefinitions().TAG_CLASS_NAME(): self.__class__.__name__,
                        logger.tagDefinitions().TAG_FUNCTION_NAME(): func.__name__,
                        logger.tagDefinitions().TAG_STATUS(): 'finished',
                    },
                    ''
                )
            except:
                # swallow exceptions for safety
                pass
            return return_val
    return wrapper
