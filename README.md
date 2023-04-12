# 项目介绍

在线评测系统 (Online Judge)系统是一个在线的判题系统，用户可以在线提交多种程序源代码(如C/C++, Java, Python)，系统对源代码进行编译和执行，并通过预先设计的测试数据或通过程序验证输出数据合法性来校验源代码正确性。

本项目在设计之初参考和借鉴了 [QingdaoU/OnlineJudge](https://github.com/QingdaoU/OnlineJudge)，在此对前辈们表达深深敬意。

YeeOnlineJudge 的后端基于Django 4，配合PostgreSQL、Redis、Celery 和 Django REST Framework 实现 Restful API。

[文档地址](https://blog.moorlands.cn/YeeOnlineJudge/)

## 功能

- [x] OnlineJudge的基本功能
- [x] 代码提交预览
- [x] 班级（组）的管理
- [x] 函数式题目与判题
- [ ] 罚时
- [ ] 博客功能
- [ ] ……

## 后端是如何工作的？

后端主要使用 Django 来支撑业务逻辑，再配合 Redis 和 Celery 处理数据统计与判题队列的异步任务。使用Django REST Framework 实现 RESTfulAPI 设计，Simple JWT 用于认证与鉴权，PostgreSQL 来完成数据持久化。
