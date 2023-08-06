# Nehushtan (נְחֻשְׁתָּן)

A toolkit for projects in Python

![PyPI](https://img.shields.io/pypi/v/nehushtan)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nehushtan)
![PyPI - License](https://img.shields.io/pypi/l/nehushtan)
![PyPI - Downloads](https://img.shields.io/pypi/dm/nehushtan)

<img src="https://github.com/sinri/nehushtan/blob/master/icon.png?raw=true" width="64" height="64"></img>

> ipse dissipavit excelsa et contrivit statuas et succidit lucos confregitque serpentem aeneum quem fecerat Moses siquidem usque ad illud tempus filii Israhel adolebant ei incensum vocavitque eum Naasthan

## History in Brief

### Released

* 0.1.2: First version on PYPI with MySQL Toolkit.
* 0.1.3: Add CLI Helper, Logger, SMTP.
* 0.1.4: Changed a lot for projects.
* 0.1.5: Rename `NehushtanArgumentParser`. Revoke the declaration of source root to rebuild the import package.
* 0.1.6: Fix packaging issue.
* 0.1.7: Fix bug, `make_condition_sql` should be replaced.
* 0.1.8: Remove shovel related static maker methods from logger class. Fix MySQL Toolkit Bug.
* 0.1.9: Fix loose throw policy in condition sql making. That has been proved very dangerous.
* 0.1.10: Support MySQL Deep Functions for one table, such as
  [INSERT ... ON DUPLICATE KEY UPDATE Statement](https://dev.mysql.com/doc/refman/8.0/en/insert-on-duplicate.html), etc.
* 0.1.11: Remove declarations of the class variables which would be initialized with instances.
* 0.1.12: MySQL Package Refines.
    1. Raise Exception when tries to get result from MySQLQueryResult but actually not generated
       yet [GitHub Issue #1](https://github.com/sinri/nehushtan/issues/1)
    2. Add Grave sign to writer methods in `MySQLTableMixin`. (Reported by Leqee Staff)
* 0.1.13: Standardize logger keys. MySQL Auto Reconnection. Database Error Display.
* 0.1.14: Fix a bug in `raw_query_for_all_dict_rows`.
* 0.1.15: Reusable `NehushtanLogger` instance by name.
* 0.1.16: Unicode JSON in Logger
* 0.1.17: Execute Many
* 0.1.18: Queue based on multiprocessing pool
* 0.1.19: Nehushtan Queue Refine
* 0.1.20: Fix Queue Command Initialization
* 0.1.22: Import Helper
* 0.1.23: Refine NoNextTaskSituation and Add grave accent to fields in writing.
* 0.1.24: Add `pid` to NehushtanQueueDelegate's two methods.
* 0.1.25: NehushtanFileLogger
* 0.1.26: NehushtanFileLogger directly output bug fix

----

* 0.2.0: New NehushtanFileLogger. Redesign NehushtanQueue with raw `Process`.
* 0.2.1: Refine NehushtanFileLogger for exception.
* 0.2.2: Refine NehushtanFileLogger for exception.
* 0.2.3: Output NehushtanFileLogger for raw output to stderr.
* 0.2.4: Add `print_as_well` to NehushtanFileLogger.
* 0.2.5: Replace `print_as_well` as `print_higher_than_this_level` in NehushtanFileLogger.

### Developing

* 0.1.27: Pending
* 0.2.6: Pending

## Notice

* [Pythonのクラスの変数に潜む地雷](https://qiita.com/sinri/items/368a489412c78cb9d4e3)
  > Python的class变量声明也不是不能当动态变量用，安全起见一定要在初始化的时候彻底初始化一下，避免id固化。