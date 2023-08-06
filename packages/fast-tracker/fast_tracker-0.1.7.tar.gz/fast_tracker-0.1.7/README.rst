======================
天眼Python探针
======================


"fast_tracker"软件包为您的应用程序进行性能监控和高级性能分析。

精确定位并解决Python应用程序性能问题，直至代码行。

Installation
------------

.. code:: bash

    $ pip install fast-tracker

Usage
-----

1. 配置好配置文件FastTracker.json.



2. Validate the agent configuration and test the connection to our data collector service.

   .. code:: bash

      $ FAST_CONFIG_FILE=FastTracker.json fast-admin run-program $YOUR_COMMAND_OPTIONS

   Examples:

   .. code:: bash

      $ FAST_CONFIG_FILE=FastTracker.json FAST_STARTUP_DEBUG=true  fast-admin run-program hug -f app.py



Resources
---------

* `文档说明 <http://doc.mypaas.com.cn/fast/03_%E6%9C%8D%E5%8A%A1%E7%AB%AF%E6%8E%A2%E9%92%88%E9%9B%86%E6%88%90/%E7%AE%80%E4%BB%8B.html>`_

License
-------

FAST for Python is free-to-use, proprietary software. Please see the LICENSE file in the distribution for details on the FAST License agreement and the licenses of its dependencies.

Copyright
---------

Copyright (c) 2019-2020 FAST, Inc. All rights reserved.